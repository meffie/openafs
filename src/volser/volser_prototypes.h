/*
 * Copyright 2000, International Business Machines Corporation and others.
 * All Rights Reserved.
 *
 * This software has been released under the terms of the IBM Public
 * License.  For details, see the LICENSE file in the top-level source
 * directory or online at http://www.openafs.org/dl/license10.html
 */

#ifndef	AFS_SRC_VOLSER_PROTOTYPES_H
#define AFS_SRC_VOLSER_PROTOTYPES_H

#include <afs/volser_compat.h>

struct nvldbentry;
struct volintInfo;

/* vsprocs.c */
extern void MapPartIdIntoName(afs_int32 partId, char *partName);

extern void MapHostToNetwork(struct nvldbentry *entry);

#endif
