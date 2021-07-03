/*
 * Copyright 2000, International Business Machines Corporation and others.
 * All Rights Reserved.
 *
 * This software has been released under the terms of the IBM Public
 * License.  For details, see the LICENSE file in the top-level source
 * directory or online at http://www.openafs.org/dl/license10.html
 */

#ifndef OPENAFS_FILEUTIL_H
#define OPENAFS_FILEUTIL_H

/* File-oriented utility functions */

/* Path normalization routines */
#define FPN_FORWARD_SLASHES 1
#define FPN_BACK_SLASHES    2

extern void
  FilepathNormalizeEx(char *path, int slashType);

/* Just a wrapper for FilepathNormalizeEx(path, FPN_FORWARD_SLASHES); */
extern void
  FilepathNormalize(char *path);

#endif /* OPENAFS_FILEUTIL_H */
