#include <afsconfig.h>
#include <afs/param.h>

#include <roken.h>

#ifdef HAVE_SYS_WAIT_H
#include <sys/wait.h>
#endif

#include <rx/rx.h>

#include <afs/cellconfig.h>

#include <tests/tap/basic.h>

#include "common.h"

/* Start up the VLserver, using the configuration in dirname, and putting our
 * logs there too.
 */

int
afstest_StartVLServer(char *dirname, pid_t *serverPid)
{
    pid_t pid;
    int status;

    pid = fork();
    if (pid == -1) {
	exit(1);
	/* Argggggghhhhh */
    } else if (pid == 0) {
	char *binPath, *logPath, *dbPath, *build;

	/* Child */
	build = getenv("BUILD");

	if (build == NULL)
	    build = "..";

	if (asprintf(&binPath, "%s/../src/tvlserver/vlserver", build) < 0 ||
	    asprintf(&logPath, "%s/VLLog", dirname) < 0 ||
	    asprintf(&dbPath, "%s/vldb", dirname) < 0) {
	    fprintf(stderr, "Out of memory building vlserver arguments\n");
	    exit(1);
	}
	execl(binPath, "vlserver",
	      "-logfile", logPath, "-database", dbPath, "-config", dirname, NULL);
	fprintf(stderr, "Running %s failed\n", binPath);
	exit(1);
    }

    if (waitpid(pid, &status, WNOHANG) != 0) {
	fprintf(stderr, "Error starting vlserver\n");
	return -1;
    }

    diag("Sleeping for a few seconds to let the vlserver startup");
    sleep(5);

    if (waitpid(pid, &status, WNOHANG) != 0) {
	fprintf(stderr, "vlserver died during startup\n");
	return -1;
    }

    *serverPid = pid;

    return 0;
}

int
afstest_StartBosServer(char *dirname, pid_t *serverPid)
{
    pid_t pid;
    int status;

    pid = fork();
    if (pid == -1) {
	exit(1);
	/* Argggggghhhhh */
    } else if (pid == 0) {
	char *binPath, *build;

	/* Child */
	build = getenv("BUILD");

	if (build == NULL)
	    build = "..";

	if (asprintf(&binPath, "%s/../src/bozo/bosserver", build) < 0) {
	    fprintf(stderr, "Out of memory building bosserver arguments\n");
	    exit(1);
	}
	/* TODO: We need to add command line options to run the bosserver in a test sandbox. */
	execl(binPath, "bosserver", "-nofork", "-skip-root-check", NULL);
	fprintf(stderr, "Running %s failed\n", binPath);
	exit(1);
    }

    if (waitpid(pid, &status, WNOHANG) != 0) {
	fprintf(stderr, "Error starting bosserver\n");
	return -1;
    }

    diag("Sleeping for a few seconds to let the bosserver startup");
    sleep(5);

    if (waitpid(pid, &status, WNOHANG) != 0) {
	fprintf(stderr, "bosserver died during startup\n");
	return -1;
    }

    *serverPid = pid;

    return 0;
}


int
afstest_StopServer(pid_t serverPid)
{
    int status;

    kill(serverPid, SIGTERM);

    waitpid(serverPid, &status, 0);

    if (WIFSIGNALED(status) && WTERMSIG(status) != SIGTERM) {
	fprintf(stderr, "Server died exited on signal %d\n", WTERMSIG(status));
	return -1;
    }
    if (WIFEXITED(status) && WEXITSTATUS(status) != 0) {
	fprintf(stderr, "Server exited with code %d\n", WEXITSTATUS(status));
	return -1;
    }
    return 0;
}

int
afstest_StartTestRPCService(const char *configPath,
			    u_short port,
			    u_short serviceId,
			    afs_int32 (*proc) (struct rx_call *))
{
    struct afsconf_dir *dir;
    struct rx_securityClass **classes;
    afs_int32 numClasses;
    int code;
    struct rx_service *service;

    dir = afsconf_Open(configPath);
    if (dir == NULL) {
        fprintf(stderr, "Server: Unable to open config directory\n");
        return -1;
    }

    code = rx_Init(htons(port));
    if (code != 0) {
	fprintf(stderr, "Server: Unable to initialise RX\n");
	return -1;
    }

    afsconf_BuildServerSecurityObjects(dir, &classes, &numClasses);
    service = rx_NewService(0, serviceId, "test", classes, numClasses,
                            proc);
    if (service == NULL) {
        fprintf(stderr, "Server: Unable to start to test service\n");
        return -1;
    }

    rx_StartServer(1);

    return 0; /* Not reached, we donated ourselves to StartServer */
}
