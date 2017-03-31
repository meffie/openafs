/*
 * Copyright 2000, International Business Machines Corporation and others.
 * All Rights Reserved.
 * 
 * This software has been released under the terms of the IBM Public
 * License.  For details, see the LICENSE file in the top-level source
 * directory or online at http://www.openafs.org/dl/license10.html
 *
 * Portions Copyright (c) 2003 Apple Computer, Inc.
 */

/*
 * This file contains sample code for the rxstats interface 
 */

#include <afsconfig.h>
#include <afs/param.h>


#ifdef AFS_NT40_ENV
#include <winsock2.h>
#include <pthread.h>
#endif
#include <limits.h>

#include <rx/rx.h>
#include <rx/rxstat.h>
#include <afs/dirpath.h>
#include <afs/cmd.h>

#include <afs/afs_Admin.h>
#include <afs/afs_clientAdmin.h>
#include <afs/afs_utilAdmin.h>

enum optionsList {
    OPT_cell,
    OPT_server,
    OPT_port,
    OPT_localauth,
};

int
rxstat_disable_process(struct cmd_syndesc *as, void *arock)
{
    int rc;
    afs_status_t st = 0;
    struct rx_connection *conn;
    char *srvrName = NULL;
    int srvrPort = 0;
    char *cellName = NULL;
    int localauth = 0;
    const char *confdir = AFSDIR_SERVER_ETC_DIR;
    void *tokenHandle;
    void *cellHandle;

    if (as->parms[OPT_cell].items)
	cellName = as->parms[OPT_cell].items->data;

    if (as->parms[OPT_server].items)
	srvrName = as->parms[OPT_server].items->data;

    if (as->parms[OPT_port].items) {
	srvrPort = atoi(as->parms[OPT_port].items->data);
	if (srvrPort <= 0 || srvrPort > USHRT_MAX) {
	    fprintf(stderr, "Invalid port number.\n");
	    return 1;
	}
    }

    if (as->parms[OPT_localauth].items)
	localauth = 1;

    rc = afsclient_Init(&st);
    if (!rc) {
	fprintf(stderr, "afsclient_Init, status %d\n", st);
	return 1;
    }

    if (localauth) {
	rc = afsclient_TokenPrint(confdir, &tokenHandle, &st);
	if (!rc) {
	    fprintf(stderr, "afsclient_TokenPrint, status %d\n", st);
	    return 1;
	}
    } else {
	rc = afsclient_TokenGetExisting(cellName, &tokenHandle, &st);
	if (!rc) {
	    fprintf(stderr, "afsclient_TokenGetExisting, status %d\n", st);
	    return 1;
	}
    }

    rc = afsclient_CellOpen(cellName, tokenHandle, &cellHandle, &st);
    if (!rc) {
	fprintf(stderr, "afsclient_CellOpen, status %d\n", st);
	return 1;
    }

    rc = afsclient_RPCStatOpenPort(cellHandle, srvrName, srvrPort, &conn,
				   &st);
    if (!rc) {
	fprintf(stderr, "afsclient_RPCStatOpenPort, status %d\n", st);
	return 1;
    }

    rc = util_RPCStatsStateDisable(conn, RXSTATS_DisableProcessRPCStats, &st);
    if (!rc) {
	fprintf(stderr, "util_RPCStatsStateDisable, status %d\n", st);
	return 1;
    }

    rc = afsclient_RPCStatClose(conn, &st);
    if (!rc) {
	fprintf(stderr, "afsclient_RPCStatClose, status %d\n", st);
	return 1;
    }

    rc = afsclient_CellClose(cellHandle, &st);
    if (!rc) {
	fprintf(stderr, "afsclient_CellClose, status %d\n", st);
	return 1;
    }

    rc = afsclient_TokenClose(tokenHandle, &st);
    if (!rc) {
	fprintf(stderr, "afsclient_TokenClose, status %d\n", st);
	return 1;
    }

    return 0;
}

int
main(int argc, char *argv[])
{
    struct cmd_syndesc *ts;

    ts = cmd_CreateSyntax(NULL, rxstat_disable_process, NULL, "rxstat disable process");
    cmd_AddParm(ts, "-cell", CMD_SINGLE, CMD_REQUIRED, "cell name");
    cmd_AddParm(ts, "-server", CMD_SINGLE, CMD_REQUIRED, "server");
    cmd_AddParm(ts, "-port", CMD_SINGLE, CMD_REQUIRED, "port");
    cmd_AddParm(ts, "-localauth", CMD_FLAG, CMD_OPTIONAL, "user server tickets");

    return cmd_Dispatch(argc, argv);
}
