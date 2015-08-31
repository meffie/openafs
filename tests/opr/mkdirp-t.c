/*
 * Copyright (c) 2015 Sine Nomine Associates. All rights reserved.
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
#include <tests/tap/basic.h>
#include <opr/mkdirp.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

void
cleanup(char *tmpdir, char *subpath)
{
    int code;
    char *sep;
    char *tsubpath = strdup(subpath);
    char path[1024];

    do {
	snprintf(path, sizeof(path), "%s/%s", tmpdir, tsubpath);
	code = rmdir(path);
	if (code) {
	    fprintf(stderr, "Failed to remove %s: errno=%d\n", path, errno);
	    exit(1);
	}
	sep = strrchr(tsubpath, '/');
	if (sep != NULL) {
	    *sep = '\0';
	}
    } while (sep);
    code = rmdir(tmpdir);
    if (code) {
	fprintf(stderr, "Failed to remove %s: errno=%d\n", path, errno);
	exit(1);
    }
    free(tsubpath);
}

int
main(void)
{
    int code;
    mode_t testmask = 0666;
    char *testpath = "one/two/three";
    char *tmpdir = NULL;
    char template[] = "/tmp/mkdirp-t-XXXXXX";
    char path[1024];
    struct stat sb;
    mode_t perms = 0;

    plan(4);

    tmpdir = mkdtemp(template);
    if (tmpdir == NULL) {
	fprintf(stderr, "Failed to create temp directory! errno=%d\n", errno);
	exit(1);
    }
    snprintf(path, sizeof(path), "%s/%s", tmpdir, testpath);
    code = opr_mkdirp(path, 0777, testmask);
    ok(code == 0, "opr_mkdirp() returned 0");

    code = stat(path, &sb);
    ok(code == 0, "stat returned 0");
    ok(code == 0 && S_ISDIR(sb.st_mode), "stat found directory");
    perms = sb.st_mode & (S_IRWXU | S_IRWXG | S_IRWXO);
    ok(code == 0 && (perms & ~testmask)==0, "permissions ok");

    cleanup(tmpdir, testpath);
    return 0;
}

