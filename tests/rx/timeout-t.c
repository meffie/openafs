/*
 * Copyright (c) 2023 Sine Nomine Associates. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR `AS IS'' AND ANY EXPRESS OR
 * IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 * IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
 * NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
 * THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include <afsconfig.h>
#include <afs/param.h>

#include <roken.h>

#include <tests/tap/basic.h>

#include <rx/rx.h>
#include <rx/rx_globals.h>
#include <afs/afsutil.h>

/*
 * Printing these stats in the test results allows a human tester to obtain
 * visual confirmation that nothing untoward has happened in the Rx stack
 * after running these tests, e.g., we haven't leaked any rx_connection structs.
 */
void
get_stats(void)
{
    /* adapted from rxdebug.c */
    int rx_version = RX_DEBUGI_VERSION_W_PACKETS;    /* latest */
    struct rx_statistics rxstats;
    osi_socket s;
    struct sockaddr_in taddr;
    afs_int32 host;
    struct in_addr hostAddr;
    short port;
    afs_int32 code;
    afs_uint32 supportedStatValues = 0;
    char hoststr[20];

    host = htonl(0x7f000001);	/* IP localhost */
    port = rx_port;		/* set by rx_Init */

    hostAddr.s_addr = host;
    afs_inet_ntoa_r(hostAddr.s_addr, hoststr);
    printf("Trying %s (port %d):\n", hoststr, ntohs(port));
    s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (s == OSI_NULLSOCKET) {
#ifdef AFS_NT40_ENV
	fprintf(stderr, "socket() failed with error %u\n", WSAGetLastError());
#else
	perror("socket");
#endif
	exit(1);
    }
    taddr.sin_family = AF_INET;
    taddr.sin_port = 0;
    taddr.sin_addr.s_addr = 0;
#ifdef STRUCT_SOCKADDR_HAS_SA_LEN
    taddr.sin_len = sizeof(struct sockaddr_in);
#endif
    code = bind(s, (struct sockaddr *)&taddr, sizeof(struct sockaddr_in));
    if (code) {
#ifdef AFS_NT40_ENV
	fprintf(stderr, "bind() failed with error %u\n", WSAGetLastError());
#else
	perror("bind");
#endif
	exit(1);
    }

    /* should gracefully handle the case where rx_stats grows */
    code = rx_GetServerStats(s, host, port, &rxstats,
			     &supportedStatValues);
    if (code < 0) {
	diag("rxstats call failed with code %d\n", code);
	exit(1);
    }
    if (code != sizeof(rxstats)) {
	struct rx_debugIn debug;
	memcpy(&debug, &rxstats, sizeof(debug));
	if (debug.type == RX_DEBUGI_BADTYPE) {
	    diag("WARNING: bad debug type (got %d)\n", code);
	} else {
	    diag("WARNING: returned Rx statistics of unexpected size (got %d)\n",
		 code);
	}
	/* handle other versions?... */
    }

    rx_PrintTheseStats(stdout, &rxstats, sizeof(rxstats),
			       0, rx_version);
}


static struct rx_securityClass *sc;

typedef struct rx_setter {
    char *name;
    void (*proc) (struct rx_connection *conn, int timeout);
} rx_setter;

#define RX_SETTER(func)	{ .name = #func, .proc = func }

static const rx_setter rx_setters[] = {
    RX_SETTER(NULL),		/* don't change a thing */
    RX_SETTER(rx_SetConnDeadTime),
    RX_SETTER(rx_SetConnIdleDeadTime),
    RX_SETTER(rx_SetConnHardDeadTime)
};

#define MAX_RX_SETTER sizeof(rx_setters)/sizeof(rx_setter)
u_short timevalues[MAX_RX_SETTER];	/* desired values for each setter */


static int
validate_timeout_invariants(int rxDead, int idleDead, int hardDead)
{
    if (RX_MINDEADTIME <= rxDead &&
	(idleDead == 0 || rxDead <= idleDead) &&
	(hardDead == 0 || (idleDead == 0 && rxDead <= hardDead) || idleDead <= hardDead))
	return 1;	/* all invariants satisfied */
    else
	return 0;	/* one or more invariants violated */
}

static void
validate_conn_timeouts(struct rx_connection *conn)
{
    int rxDead = rx_GetConnDeadTime(conn);
    int idleDead = rx_GetConnIdleDeadTime(conn);
    int hardDead = rx_GetConnHardDeadTime(conn);

    ok(validate_timeout_invariants(rxDead, idleDead, hardDead),
	"conn invariants satisfied: rxDead=%d, idleDead=%d, hardDead=%d",
	rxDead, idleDead, hardDead);
}

/*
 * Yes, I'm referencing global arrays here.
 * Relax, they're just tests.
 */
static void
run_setter(struct rx_connection *conn, int index)
{
    void (*setter) (struct rx_connection *conn, int timeout);
    int setval;

    setter = rx_setters[index].proc;
    setval = timevalues[index];
    if (setter != NULL) {
	(setter) (conn, setval);
    }
}

/*
 * For a given tuple of rxDead, idleDead, and hardDead values, set them over
 * all possible orderings, and validate the results for each ordering.
 */
static void
test_timevalues(u_short rxDead, u_short idleDead, u_short hardDead)
{
    int first, second, third;
    struct rx_connection *conn = NULL;

    diag("initial values: rxDead=%d, idleDead=%d, hardDead=%d",
	    rxDead, idleDead, hardDead);
    timevalues[0] = 0;
    timevalues[1] = rxDead;
    timevalues[2] = idleDead;
    timevalues[3] = hardDead;

    /*
     * Iterate over all possible orderings of the timeout setters, because each
     * setter calls rxi_CheckConnTimeouts, whose side effects are the actual
     * target of each iteration of this test.
     */
    for (first = 0; first < 4; first++) {
	for (second = 0; second < 4; second++) {
	    for (third = 0; third < 4; third++) {

		diag("trial values: rxDead=%d, idleDead=%d, hardDead=%d",
			rxDead, idleDead, hardDead);
		diag("trial setter order: %s=%d, %s=%d, %s=%d",
			rx_setters[first].name, timevalues[first],
			rx_setters[second].name, timevalues[second],
			rx_setters[third].name, timevalues[third]);

		/*
		 * Each test obtains a new client connection to ensure a consistent
		 * initial state.
		 * rx_NewConnection current defaults:
		 *   rx_SetConnDeadTime		secondsUntilDead    12s  from rx_Init()
		 *   rx_SetConnIdleDeadTime	idleDeadTime	    0
		 *   rx_SetConnHardDeadTime	hardDeadTime	    0
		*/
		conn = rx_NewConnection(INADDR_LOOPBACK, htons(1), 1,
					sc, RX_SECIDX_NULL);
		opr_Assert(conn != NULL);

		/* Invoke the setters in the specified order for this case. */
		run_setter(conn, first);
		run_setter(conn, second);
		run_setter(conn, third);

		/*
		 * Note that this only checks that the rx timeout invariants are
		 * met.  It does not attempt to verify that we got the timeouts
		 * specified for this trial, because 1) a setter may have been
		 * skipped ("NULL") or 2) rxi_CheckConnTimeouts may have
		 * changed any of the requested rx timeout values in order to
		 * preserve the invariants.
		 */
		validate_conn_timeouts(conn);

		rx_PutConnection(conn);
	    }
	}
    }
}


int
main(void)
{
    u_short rxDead, idleDead, hardDead;
    int code;
    int maxTime = 10;	/* 10s should suffice for all possible permutations of timeout value orderings */
    int nTests;		/* number of tests in a single call to test_timevalues() */

    code = rx_Init(0);	/* rx_connDeadTime = RX_DEAULT_DEAD_TIME = 12s */
    if (code != 0)
	skip_all("rx Init() failed with code %d\n", code);

    sc = rxnull_NewClientSecurityObject();	/* safe to reuse for all conns */

    nTests = MAX_RX_SETTER * MAX_RX_SETTER * MAX_RX_SETTER;
    plan(maxTime * maxTime * maxTime * nTests);


    for (rxDead=0; rxDead<maxTime; rxDead++) {
	for (idleDead=0; idleDead<maxTime; idleDead++) {
	    for (hardDead=0; hardDead<maxTime; hardDead++) {
		test_timevalues(rxDead, idleDead, hardDead);
	    }
	}
    }

    get_stats();    /* mostly to check for conn leaks */

    return 0;
}
