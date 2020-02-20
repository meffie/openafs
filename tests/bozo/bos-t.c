
#include <afsconfig.h>
#include <afs/param.h>
#include <roken.h>
#include <sys/wait.h>
#include <rx/rx.h>
#include <ubik.h>
#include <afs/com_err.h>
#include <afs/cellconfig.h>
#include <tests/tap/basic.h>
#include "common.h"

void
bos(char *dirname)
{
    pid_t pid;
    int outpipe[2];
    int status;
    char *buffer;
    size_t len;

    /* Now we need to run vos ListAddrs and see what happens ... */
    if (pipe(outpipe) < 0) {
	perror("pipe");
	exit(1);
    }
    pid = fork();
    if (pid == 0) {
	char *build, *binPath;

	dup2(outpipe[1], STDOUT_FILENO); /* Redirect stdout into pipe */
	close(outpipe[0]);
	close(outpipe[1]);

	build = getenv("BUILD");
	if (build == NULL)
	    build = "..";

	if (asprintf(&binPath, "%s/../src/bozo/bos", build) < 0) {
	    fprintf(stderr, "Out of memory building bos arguments\n");
	    exit(1);
	}
	execl(binPath, "bos", "status", "localhost", NULL);
	exit(1);
    }
    close(outpipe[1]);
    buffer = malloc(4096);
    len = read(outpipe[0], buffer, 4096);
    waitpid(pid, &status, 0);
    buffer[len]='\0';
    free(buffer);
}

int
main(int argc, char **argv)
{
    int rc = 0;
    int code;
    char *dirname;
    struct afsconf_dir *dir;
    pid_t serverPid = 0;
    char *argv0 = afstest_GetProgname(argv);

    plan(1);

    afstest_SkipTestsIfBadHostname();
    afstest_SkipTestsIfServerRunning("afs3-bos");

    dirname = afstest_BuildTestConfig();
    dir = afsconf_Open(dirname);
    code = afstest_AddDESKeyFile(dir);
    if (code) {
	afs_com_err(argv0, code, "while adding test DES keyfile");
	rc = 1;
	goto out;
    }

    code = afstest_StartBosServer(dirname, &serverPid);
    if (code) {
	afs_com_err(argv0, code, "while starting the bosserver");
	rc = 1;
	goto out;
    }

out:
    if (serverPid != 0) {
	code = afstest_StopServer(serverPid);
	is_int(0, code, "Server exited cleanly");
    }

    afstest_UnlinkTestConfig(dirname);
    return rc;
}
