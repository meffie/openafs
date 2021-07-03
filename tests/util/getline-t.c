/*
 * Copyright 2021, Sine Nomine Associates and others.
 * All Rights Reserved.
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

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <afs/afsutil.h>
#include <tests/tap/basic.h>


void
stdin_example(void)
{
    char *p = NULL;
    ssize_t len;
    size_t n = 0;

//    plan_lazy();

    while ((len = getline(&p, &n, stdin)) != -1)
	(void)printf("%zd %s", len, p);
    free(p);
}

int
main(int argc, char **argv)
{
    int code;
    int fd;
    char *filename = NULL;
    FILE *f = NULL;
    int i;

    code = asprintf(&filename, "/tmp/afs_getline_XXXXXX");
    if (code < 0)
	sysbail("out of memory");

    fd = mkstemp(filename);
    if (fd < 0)
	sysbail("mkstemp");

    diag("filename=%s", filename);

    f = fdopen(fd, "w+");
    if (f == NULL)
	sysbail("fdopen");

    fprintf(f, "hello world\n");
    fprintf(f, "yet another line\n");
    fprintf(f, "\n"); /* empty */
    fprintf(f, "a very long line: ");
    for (i = 0; i<1024; i++) {
	fprintf(f, "%s", "1234567890");
    }
    fprintf(f, "\n");
    fprintf(f, "last\n");

    fseek(f, 0, SEEK_CUR);

    len = getline(&p, &n, f);

    //unlink(filename);
    free(filename);
    fclose(f);
    return 0;
}
