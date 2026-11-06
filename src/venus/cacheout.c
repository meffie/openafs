/*
 * Copyright 2000, International Business Machines Corporation and others.
 * All Rights Reserved.
 *
 * This software has been released under the terms of the IBM Public
 * License.  For details, see the LICENSE file in the top-level source
 * directory or online at http://www.openafs.org/dl/license10.html
 */

#include <afsconfig.h>
#include <afs/param.h>

#include <roken.h>

#include <ctype.h>

#include <afs/auth.h>
#include <afs/cmd.h>
#include <afs/cellconfig.h>
#include <afs/afsint.h>
#include <afs/vlserver.h>
#include <rx/rx.h>
#include <rx/xdr.h>
#include <ubik.h>
#include <afs/kauth.h>
#include <afs/afsutil.h>
#include <afs/vldbint.h>

static afs_int32 server_count = 0;
static afs_int32 server_id[256];	/* file servers in network byte order */

static struct ubik_client *client;

static struct rx_securityClass *sc;
static int scindex;

enum optionsList {
    OPT_id,
    OPT_ip,
    OPT_cell,
    OPT_noauth,
    OPT_localauth,
    OPT_encrypt,
    OPT_dryrun,
};

/*!
 * Obtain list of file servers as known to VLDB. These may
 * not actually be configured as file servers in the cell.
 *
 * \retval 0	success
 *
 * \post    globals server_count and server_id[] are updated.
 */
static afs_int32
ListServers(void)
{
    afs_int32 code;
    int i;
    struct VLCallBack vlcb;
    bulkaddrs addrs, m_addrs;
    afs_uint32 ip;
    afsUUID m_uuid;
    afs_int32 m_uniq = 0;
    afs_int32 m_nentries;
    ListAddrByAttributes m_attrs;
    int server_ix = 0;	/* current index into server_id[] */

    memset(&addrs, 0, sizeof(addrs));
    code =
	ubik_VL_GetAddrs(client, 0, 0, 0, &vlcb,
			 &server_count, &addrs);
    if (code != 0) {
	printf("Fatal error: could not get list of file servers\n");
	return 1;
    }

    if (addrs.bulkaddrs_len < server_count) {
	server_count = addrs.bulkaddrs_len;
    }
    /* Record any legacy IPv4 entries first. */
    for (i = 0; i < server_count; ++i) {
	ip = addrs.bulkaddrs_val[i];

	if (((ip & 0xff000000) == 0xff000000) && ((ip & 0xffff) != 0)) {
	    continue;	/* MH entries will be recorded later */
	}
	/* Record an IPv4 entry now. */
	server_id[server_ix++] = htonl(ip);
    }

    /*
     * We do NOT know if there were any interleaved unoccupied slots in the
     * VLDB fileserver list due to previous 'vos remaddr' commands.
     * Unfortunately, VL_GetAddrsU does not distinguish between empty slots and
     * legacy IPv4 slots - it returns VL_NOENT for both.
     *
     * m_attrs.index is an index into the VLDB fileserver list, which is
     * indexed by one.
     */
    for (i = 1; server_ix < server_count; ++i) {
	memset(&m_attrs, 0, sizeof(m_attrs));
	memset(&m_addrs, 0, sizeof(m_addrs));

	m_attrs.Mask = VLADDR_INDEX;
	m_attrs.index = i;
	m_nentries = 0;

	code = ubik_VL_GetAddrsU(client, 0, &m_attrs, &m_uuid, &m_uniq,
				 &m_nentries, &m_addrs);

	switch (code) {
	case 0:
	    if (m_addrs.bulkaddrs_len == 0) {
		printf("Slot %d: Error %d getting multihomed addresses for server %d\n",
		       i, code, server_ix);
		code = 1;
		goto done;
	    }
	    /* Success - we found an MH entry.  Use its first IPv4 address. */
	    server_id[server_ix++] = htonl(m_addrs.bulkaddrs_val[0]);
	    break;
	case VL_NOENT:
	    /*
	     * Ignore this; it's either a blank or legacy IPv4 entry in the
	     * VLDB server list.
	     */
	    code = 0;	/* not an error */
	    continue;
	case VL_INDEXERANGE:
	    /* We've reached the end of the server list. */
	    server_count = server_ix;	/* adjust count of found MH entries */
	    code = 0;	/* not an error */
	    goto done;
	default:
	    printf("Slot %d: Error %d getting multihomed addresses for server %d\n",
		   i, code, server_ix);
	    goto done;
	}
    }
    server_count = server_ix;
  done:
    return code;
}

/*!
 * Print the arguments of a FlushCPS() call.
 *
 * \param[in] server  file server address (network byte order)
 * \param[in] port    file server port
 * \param[in] vid     list of user ids
 * \param[in] ipa     list of IPv4 addresses (network byte order)
 * \param[in] dryrun  print a "[dryrun] " prefix
 */
static void
PrintFlushCPS(afs_uint32 server, int port, struct ViceIds *vid,
	      struct IPAddrs *ipa, int dryrun)
{
    char hoststr[16];
    const char *prefix;
    int i;

    if (dryrun) {
	prefix = "[dryrun] ";
    } else {
	prefix = "";
    }

    printf("%sCalling FlushCPS() on %s:%d; ids=[",
	   prefix, afs_inet_ntoa_r(server, hoststr), port);
    for (i = 0; i < vid->ViceIds_len; i++) {
	if (i > 0) {
	    printf(", ");
	}
	printf("%ld", afs_printable_int32_ld(vid->ViceIds_val[i]));
    }
    printf("], ips=[");
    for (i = 0; i < ipa->IPAddrs_len; i++) {
	if (i > 0) {
	    printf(", ");
	}
	printf("%s", afs_inet_ntoa_r(ipa->IPAddrs_val[i], hoststr));
    }
    printf("]\n");
    fflush(stdout);
}

/*!
 * Call FlushCPS() on a file server.
 *
 * Print one line to stdout showing the file server, user ids, and IP
 * addresses before the call. For a dry run, print the line but do not
 * make the call.
 *
 * \param[in] server  file server address (network byte order)
 * \param[in] vid     list of user ids
 * \param[in] ipa     list of IPv4 addresses (network byte order)
 * \param[in] dryrun  print the call without making it
 *
 * \return 0 on success, 1 on connection failure, otherwise the RPC error code
 */
static int
FlushCPS(afs_uint32 server, struct ViceIds *vid, struct IPAddrs *ipa,
	 int dryrun)
{
    afs_int32 code;
    struct rx_connection *conn;
    afs_int32 port = AFSCONF_FILEPORT;
    char hoststr[16];
    afs_int32 spare1 = 0;
    afs_int32 spare2, spare3;

    conn = rx_NewConnection(server, htons(port), 1, sc, scindex);
    if (conn == NULL) {
	fprintf(stderr, "Could not connect to file server %s\n",
		afs_inet_ntoa_r(server, hoststr));
	return 1;
    }

    PrintFlushCPS(server, port, vid, ipa, dryrun);

    /*
     * Invalidate the file server CPS cache for the specified user ids
     * and host addresses, unless in dryrun mode.
     */
    if (dryrun) {
	code = 0;
    } else {
	code = RXAFS_FlushCPS(conn, vid, ipa, spare1, &spare2, &spare3);
	if (code != 0) {
	    fprintf(stderr, "Failed to invalidate file server %s cache; code %ld\n",
		    afs_inet_ntoa_r(server, hoststr),
		    afs_printable_int32_ld(code));
	}
    }

    rx_DestroyConnection(conn);
    return code;
}

/*!
 * Invalidate the file server CPS cache for the given users and hosts.
 *
 * Call FlushCPS() on each file server listed in the VLDB. The users are
 * given as AFS user ids (for example, from "pts examine") and the hosts
 * as IP addresses (no wildcards).
 */
static int
InvalidateCache(struct cmd_syndesc *as, void *arock)
{
    afs_int32 code = 0;
    struct cmd_item *ids = NULL;
    struct cmd_item *ips = NULL;
    int dryrun;
    struct cmd_item *u;
    int i;
    int err = 0;
    afs_int32 id[256];
    afs_int32 ip[256];
    struct ViceIds vid;
    struct IPAddrs ipa;

    cmd_OptionAsList(as, OPT_id, &ids);
    cmd_OptionAsList(as, OPT_ip, &ips);
    dryrun = cmd_OptionPresent(as, OPT_dryrun);

    /* Require at least one user id or IP address. */
    if (ids == NULL && ips == NULL) {
	fprintf(stderr, "Must specify at least one -id or -ip.\n");
	return 1;
    }

    code = ListServers();
    if (code != 0) {
	return code;
    }

    /* Convert the -id arguments to user ids. */
    for (i = 0, u = ids; i < 255 && u != NULL; ++i, u = u->next) {
	code = util_GetInt32(u->data, &id[i]);
	if (code != 0) {
	    printf("Fatal error: bad conversion to long for %s\n", u->data);
	    return code;
	}
    }

    id[i] = 0;
    vid.ViceIds_len = i;
    vid.ViceIds_val = id;

    /* Convert the -ip arguments to IP addresses, in network byte order. */
    for (i = 0, u = ips; i < 255 && u != NULL; ++i, u = u->next) {
	ip[i] = inet_addr(u->data);
    }

    ip[i] = 0;
    ipa.IPAddrs_len = i;
    ipa.IPAddrs_val = ip;

    for (i = 0; i < server_count; ++i) {
	if (server_id[i] == 0) {
	    err = 1;
	    continue;
	}
	code = FlushCPS(server_id[i], &vid, &ipa, dryrun);
	if (code != 0) {
	    err = 1;
	}
    }
    return err;
}

/*!
 * List the file servers in the cell.
 *
 * Print the number of file servers listed in the VLDB, followed by the
 * host name of each one, or its address if the name cannot be found.
 */
static int
GetServerList(struct cmd_syndesc *as, void *arock)
{
    int code;
    int i;

    code = ListServers();
    if (code != 0) {
	return (code);
    }

    printf("There are %d file servers in the cell\n\n", server_count);
    fflush(stdout);
    for (i = 0; i < server_count; ++i) {
	printf("%s\n", hostutil_GetNameByINet(server_id[i]));
    }
    fflush(stdout);

    return code;
}

/*!
 * Set up the security object and the VL server connections before
 * running a command.
 *
 * The command is run in the local cell, unless -cell is given.
 */
static int
MyBeforeProc(struct cmd_syndesc *as, void *arock)
{
    char *tcell = NULL;
    char confdir[200];
    struct afsconf_dir *tdir;
    struct afsconf_cell info;
    struct rx_connection *serverconns[MAXSERVERS];
    afs_int32 code, i;
    rxkad_level sclevel = rxkad_auth;

    sprintf(confdir, "%s", AFSDIR_CLIENT_ETC_DIRPATH);
    if (cmd_OptionPresent(as, OPT_localauth)) {
	sprintf(confdir, "%s", AFSDIR_SERVER_ETC_DIRPATH);
    }

    if (cmd_OptionPresent(as, OPT_encrypt)) {
	sclevel = rxkad_crypt;
    }

    code = rx_Init(0);
    if (code != 0) {
	printf("Warning: could not initialize network communication.\n");
	return 1;
    }

    sc = rxnull_NewClientSecurityObject();
    scindex = 0;

    tdir = afsconf_Open(confdir);
    if (tdir == NULL) {
	printf("Warning: could not get cell configuration.\n");
	return 1;
    }

    cmd_OptionAsString(as, OPT_cell, &tcell);
    code = afsconf_GetCellInfo(tdir, tcell, AFSCONF_VLDBSERVICE, &info);
    free(tcell);
    if (code != 0 || info.numServers > MAXSERVERS) {
	printf("Warning: could not init cell info.\n");
	return 1;
    }

    if (cmd_OptionPresent(as, OPT_localauth)) {
	if (sclevel == rxkad_crypt) {
	    code = afsconf_ClientAuthSecure(tdir, &sc, &scindex);
	} else {
	    code = afsconf_ClientAuth(tdir, &sc, &scindex);
	}
	if (code != 0 || scindex == 0) {
	    afsconf_Close(tdir);
	    fprintf(stderr, "Could not get security object for -localauth (code: %d)\n",
		    code);
	    return -1;
	}

    } else if (!cmd_OptionPresent(as, OPT_noauth)) {
	struct ktc_principal sname;
	struct ktc_token ttoken;

	strcpy(sname.cell, info.name);
	sname.instance[0] = '\0';
	strcpy(sname.name, "afs");

	code = ktc_GetToken(&sname, &ttoken, sizeof(ttoken), NULL);
	if (code != 0) {
	    fprintf(stderr, "Could not get afs tokens, running unauthenticated\n");
	} else {
	    scindex = 2;
	    sc = rxkad_NewClientSecurityObject(sclevel, &ttoken.sessionKey,
					       ttoken.kvno, ttoken.ticketLen,
					       ttoken.ticket);
	}
    }

    for (i = 0; i < info.numServers; ++i) {
	serverconns[i] =
	    rx_NewConnection(info.hostAddr[i].sin_addr.s_addr,
			     info.hostAddr[i].sin_port, USER_SERVICE_ID, sc,
			     scindex);
    }
    for (; i < MAXSERVERS; ++i) {
	serverconns[i] = (struct rx_connection *)0;
    }
    code = ubik_ClientInit(serverconns, &client);
    if (code != 0) {
	printf("Warning: could not initialize RPC interface.\n");
	return 1;
    }
    return 0;
}

int
main(int argc, char **argv)
{
    afs_int32 code = 0;
    struct cmd_syndesc *ts;

#ifdef AFS_AIX32_ENV
    struct sigaction nsa;

    sigemptyset(&nsa.sa_mask);
    nsa.sa_handler = SIG_DFL;
    nsa.sa_flags = SA_FULLDUMP;
    sigaction(SIGSEGV, &nsa, NULL);
#endif

    /*
     * Connect to the VL servers before running each command.
     */
    cmd_SetBeforeProc(MyBeforeProc, NULL);

    ts = cmd_CreateSyntax("initcmd", InvalidateCache, NULL, 0,
			  "invalidate server ACL cache");
    cmd_AddParmAtOffset(ts, OPT_id, "-id", CMD_LIST, CMD_OPTIONAL,
			"user identifier");
    cmd_AddParmAtOffset(ts, OPT_ip, "-ip", CMD_LIST, CMD_OPTIONAL,
			"IP address");
    cmd_AddParmAtOffset(ts, OPT_cell, "-cell", CMD_SINGLE, CMD_OPTIONAL,
			"cell name");
    cmd_AddParmAtOffset(ts, OPT_noauth, "-noauth", CMD_FLAG, CMD_OPTIONAL,
			"don't authenticate");
    cmd_AddParmAtOffset(ts, OPT_localauth, "-localauth", CMD_FLAG,
			CMD_OPTIONAL, "user server tickets");
    cmd_AddParmAtOffset(ts, OPT_encrypt, "-encrypt", CMD_FLAG, CMD_OPTIONAL,
			"encrypt commands");
    cmd_AddParmAtOffset(ts, OPT_dryrun, "-dryrun", CMD_FLAG, CMD_OPTIONAL,
			"list what would be done, don't do it");
    cmd_CreateAlias(ts, "ic");

    ts = cmd_CreateSyntax("listservers", GetServerList, NULL, 0,
			  "list servers in the cell");
    cmd_AddParmAtOffset(ts, OPT_cell, "-cell", CMD_SINGLE, CMD_OPTIONAL,
			"cell name");
    cmd_CreateAlias(ts, "ls");

    code = cmd_Dispatch(argc, argv);

    rx_Finalize();

    exit(code);
}
