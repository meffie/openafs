/*
 * Copyright 2000, International Business Machines Corporation and others.
 * All Rights Reserved.
 *
 * This software has been released under the terms of the IBM Public
 * License.  For details, see the LICENSE file in the top-level source
 * directory or online at http://www.openafs.org/dl/license10.html
 */

/* File-oriented utility functions */

#include <afsconfig.h>
#include <afs/param.h>
#include <afs/stds.h>

#include <roken.h>

#include <stddef.h>

#ifdef AFS_NT40_ENV
#include "errmap_nt.h"
#endif

#include "fileutil.h"

/*
 * FilepathNormalizeEx() -- normalize file path; i.e., use only forward (or only
 *     backward) slashes, remove multiple and trailing slashes.
 */
void
FilepathNormalizeEx(char *path, int slashType)
{
    short bWasSlash = 0;
    char *pP, *pCopyFrom;
    char slash = '/';		/* Default to forward slashes */

    if (slashType == FPN_BACK_SLASHES)
	slash = '\\';

    if (path != NULL) {
	/* use only forward slashes; remove multiple slashes */
	for (pP = pCopyFrom = path; *pCopyFrom != '\0'; pCopyFrom++) {
	    if ((*pCopyFrom == '/') || (*pCopyFrom == '\\')) {
		if (!bWasSlash) {
		    *pP++ = slash;
		    bWasSlash = 1;
		}
	    } else {
		*pP++ = *pCopyFrom;
		bWasSlash = 0;
	    }
	}
	*pP = '\0';

	/* strip off trailing slash (unless specifies root) */
	pP--;
	if ((*pP == slash) && (pP != path)) {
#ifdef AFS_NT40_ENV
	    /* check for "X:/" */
	    if (*(pP - 1) != ':') {
		*pP = '\0';
	    }
#else
	    *pP = '\0';
#endif
	}
    }
}


void
FilepathNormalize(char *path)
{
    FilepathNormalizeEx(path, FPN_FORWARD_SLASHES);
}
