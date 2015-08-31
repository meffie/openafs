/*
 * Copyright (c) 2009 Sine Nomine Associates. All rights reserved.
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
#include <sys/stat.h>
#include <sys/types.h>

#ifdef AFS_NT40_ENV
 #define PATH_SEP '\\'
#else
 #define PATH_SEP '/'
#endif

/*!
 * Make directory with parents.
 *
 * \note The pmode and cmode masks specify the permissions to set on newly
 *       created directories. These are modified by the umask in the usual
 *       way, i.e. mode & ~umask & 0777.
 *
 * \param[in] path    directory path to create
 * \param[in] pmode   permissions mask for intermediate directories
 * \param[in] cmode   permissions mask for the last directory in the path
 * \return            0 on success
 */
int
opr_mkdirp(const char *path, mode_t pmode, mode_t cmode)
{
    struct stat stats;
    int error = 0;
    char *tdir;
    char *p;
    size_t len;

    tdir = strdup(path);
    if (!tdir) {
	return ENOMEM;
    }

    /* strip trailing slashes */
    len = strlen(tdir);
    if (!len) {
	return 0;
    }
    p = tdir + len - 1;
    while (p != tdir && *p == PATH_SEP) {
	*p-- = '\0';
    }

    p = tdir;
#ifdef AFS_NT40_ENV
    /* skip drive letter */
    if (isalpha(p[0]) && p[1] == ':') {
        p += 2;
    }
#endif
    /* skip leading slashes */
    while (*p == PATH_SEP) {
	p++;
    }

    /* create parent directories with default perms */
    p = strchr(p, PATH_SEP);
    while (p) {
	*p = '\0';
	if (stat(tdir, &stats) != 0 || !S_ISDIR(stats.st_mode)) {
	    if (mkdir(tdir, pmode) != 0) {
		error = errno;
		goto done;
	    }
	}
	*p++ = PATH_SEP;

	/* skip back to back slashes */
	while (*p == PATH_SEP) {
	    p++;
	}
	p = strchr(p, PATH_SEP);
    }

    /* set required perms on the last path component */
    if (stat(tdir, &stats) != 0 || !S_ISDIR(stats.st_mode)) {
	if (mkdir(tdir, cmode) != 0) {
	    error = errno;
	}
    }

  done:
    free(tdir);
    return error;
}
