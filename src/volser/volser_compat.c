/*
 * Copyright 2000, International Business Machines Corporation and others.
 * All Rights Reserved.
 *
 * This software has been released under the terms of the IBM Public
 * License.  For details, see the LICENSE file in the top-level source
 * directory or online at http://www.openafs.org/dl/license10.html
 */

#include <afsconfig.h>
#include <afs/param.h>
#include <roken.h>
#include <afs/stds.h>
#include <rx/rx_queue.h>
#include <rx/rx.h>
#include <afs/vlserver.h>
#include <afs/afsint.h>
#include <afs/ihandle.h>
#include <afs/vnode.h>
#include <afs/volume.h>
#include "volser.h"
#include "volint.h"
#include "volser_internal.h"
#include "volser_compat.h"

/*
 * Compatibility wrappers for libvolser.
 *
 * Note: The following functions are deprecated. Please do not
 *       use them in new programs. They are provided for older
 *       programs which are linked with libvolser.
 */

/* vsproc.c */

static struct rx_securityClass *uvclass = 0;
static int uvindex = -1;
/* called by VLDBClient_Init to set the security module to be used in the RPC */
int
UV_SetSecurity(struct rx_securityClass *as, afs_int32 aindex)
{
    uvindex = aindex;
    uvclass = as;
    return 0;
}

/* bind to volser on <port> <aserver> */
/* takes server address in network order, port in host order.  dumb */
struct rx_connection *
UV_Bind(afs_uint32 aserver, afs_int32 port)
{
    struct rx_connection *tc;

    tc = rx_NewConnection(aserver, htons(port), VOLSERVICE_ID, uvclass,
			  uvindex);
    return tc;
}

int
UV_NukeVolume(afs_uint32 server, afs_int32 partid, afs_uint32 volid)
{
    struct rx_connection *tconn;
    afs_int32 code;

    tconn = UV_Bind(server, AFSCONF_VOLUMEPORT);
    if (tconn) {
	code = AFSVolNukeVolume(tconn, partid, volid);
	rx_DestroyConnection(tconn);
    } else
	code = 0;
    return code;
}

int
UV_PartitionInfo64(afs_uint32 server, char *pname,
		   struct diskPartition64 *partition)
{
    struct rx_connection *conn;
    afs_int32 code = 1;

    conn = UV_Bind(server, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_PartitionInfo64(conn, pname, partition);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_CreateVolume(afs_uint32 aserver, afs_int32 apart, char *aname,
		afs_uint32 * anewid)
{
    afs_int32 aquota = 5000;
    afs_int32 aspare1 = 0;
    afs_int32 aspare2 = 0;
    afs_int32 aspare3 = 0;
    afs_int32 aspare4 = 0;
    afs_uint32 roid = 0;
    afs_uint32 bkid = 0;

    *anewid = 0;
    return vs_CreateVolume(aserver, apart, aname, aquota, aspare1,
			   aspare2, aspare3, aspare4, anewid, &roid, &bkid);
}

int
UV_CreateVolume2(afs_uint32 aserver, afs_int32 apart, char *aname,
		 afs_int32 aquota, afs_int32 aspare1, afs_int32 aspare2,
		 afs_int32 aspare3, afs_int32 aspare4, afs_uint32 * anewid)
{
    afs_uint32 roid = 0;
    afs_uint32 bkid = 0;

    return vs_CreateVolume(aserver, apart, aname, aquota, aspare1, aspare2,
	aspare3, aspare4, anewid, &roid, &bkid);
}

int
UV_CreateVolume3(afs_uint32 aserver, afs_int32 apart, char *aname,
		 afs_int32 aquota, afs_int32 aspare1, afs_int32 aspare2,
		 afs_int32 aspare3, afs_int32 aspare4, afs_uint32 * anewid,
		 afs_uint32 * aroid, afs_uint32 * abkid)
{
    return vs_CreateVolume(aserver, apart, aname,
		 aquota, aspare1, aspare2,
		 aspare3, aspare4, anewid,
		 aroid, abkid);
}

int
UV_AddVLDBEntry(afs_uint32 aserver, afs_int32 apart, char *aname,
		afs_uint32 aid)
{
    return vs_AddVLDBEntry(aserver, apart, aname, aid);
}

int
UV_DeleteVolume(afs_uint32 aserver, afs_int32 apart, afs_uint32 avolid)
{
    return vs_DeleteVolume(aserver, apart, avolid);
}

int
UV_ConvertRO(afs_uint32 server, afs_uint32 partition, afs_uint32 volid,
		struct nvldbentry *entry)
{
    return vs_ConvertRO(server, partition, volid, entry);
}

int
UV_MoveVolume2(afs_uint32 afromvol, afs_uint32 afromserver, afs_int32 afrompart,
	       afs_uint32 atoserver, afs_int32 atopart, int flags)
{
    return vs_MoveVolume(afromvol, afromserver, afrompart,
	       atoserver, atopart, flags);
}

int
UV_MoveVolume(afs_uint32 afromvol, afs_uint32 afromserver, afs_int32 afrompart,
	      afs_uint32 atoserver, afs_int32 atopart)
{
    return vs_MoveVolume(afromvol, afromserver, afrompart,
			  atoserver, atopart, 0);
}

int
UV_CopyVolume2(afs_uint32 afromvol, afs_uint32 afromserver, afs_int32 afrompart,
	       char *atovolname, afs_uint32 atoserver, afs_int32 atopart,
	       afs_uint32 atovolid, int flags)
{
    return vs_CopyVolume(afromvol, afromserver, afrompart,
	       atovolname, atoserver, atopart,
	       atovolid, flags);
}

int
UV_CopyVolume(afs_uint32 afromvol, afs_uint32 afromserver, afs_int32 afrompart,
	      char *atovolname, afs_uint32 atoserver, afs_int32 atopart)
{
    return vs_CopyVolume(afromvol, afromserver, afrompart,
                          atovolname, atoserver, atopart, 0, 0);
}

int
UV_BackupVolume(afs_uint32 aserver, afs_int32 apart, afs_uint32 avolid)
{
    return vs_BackupVolume(aserver, apart, avolid);
}

int
UV_CloneVolume(afs_uint32 aserver, afs_int32 apart, afs_uint32 avolid,
	       afs_uint32 acloneid, char *aname, int flags)
{
    return vs_CloneVolume(aserver, apart, avolid, acloneid, aname, flags);
}

int
UV_ReleaseVolume(afs_uint32 afromvol, afs_uint32 afromserver,
		 afs_int32 afrompart, int flags)
{
    return vs_ReleaseVolume(afromvol, afromserver, afrompart, flags);
}

int
UV_DumpVolume(afs_uint32 afromvol, afs_uint32 afromserver, afs_int32 afrompart,
	      afs_int32 fromdate,
	      afs_int32(*DumpFunction) (struct rx_call *, void *), void *rock,
	      afs_int32 flags)
{
    return vs_DumpVolume(afromvol, afromserver, afrompart,
	      fromdate, DumpFunction, rock, flags);
}

int
UV_DumpClonedVolume(afs_uint32 afromvol, afs_uint32 afromserver,
		    afs_int32 afrompart, afs_int32 fromdate,
		    afs_int32(*DumpFunction) (struct rx_call *, void *),
		    void *rock, afs_int32 flags)
{
    return vs_DumpClonedVolume(afromvol, afromserver, afrompart, fromdate, DumpFunction, rock, flags);
}

int
UV_RestoreVolume2(afs_uint32 toserver, afs_int32 topart, afs_uint32 tovolid,
		  afs_uint32 toparentid, char tovolname[], int flags,
		  afs_int32(*WriteData) (struct rx_call *, void *),
		  void *rock)
{
    return vs_RestoreVolume(toserver, topart, tovolid,
			    toparentid, tovolname, flags,
			    WriteData, rock);
}

int
UV_RestoreVolume(afs_uint32 toserver, afs_int32 topart, afs_uint32 tovolid,
		 char tovolname[], int flags,
		 afs_int32(*WriteData) (struct rx_call *, void *),
		 void *rock)
{
    afs_uint32 toparentid = 0;

    return vs_RestoreVolume(toserver, topart, tovolid,
			    toparentid, tovolname, flags,
			    WriteData, rock);
}

int
UV_LockRelease(afs_uint32 volid)
{
    return vs_LockRelease(volid);
}

int
UV_AddSite(afs_uint32 server, afs_int32 part, afs_uint32 volid,
	   afs_int32 valid)
{
    afs_uint32 rovolid = 0;

    return vs_AddSite(server, part, volid, rovolid, valid);
}

int
UV_AddSite2(afs_uint32 server, afs_int32 part, afs_uint32 volid,
	    afs_uint32 rovolid, afs_int32 valid)
{
    return vs_AddSite(server, part, volid, rovolid, valid);
}

int
UV_RemoveSite(afs_uint32 server, afs_int32 part, afs_uint32 volid)
{
    return vs_RemoveSite(server, part, volid);
}

int
UV_ChangeLocation(afs_uint32 server, afs_int32 part, afs_uint32 volid)
{
    return vs_ChangeLocation(server, part, volid);
}

int
UV_ListPartitions(afs_uint32 aserver, struct partList *ptrPartList,
		  afs_int32 * cntp)
{
    int code = 0;
    struct rx_connection *conn;

    conn = UV_Bind(aserver, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_ListPartitions(conn, ptrPartList, cntp);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_ZapVolumeClones(afs_uint32 aserver, afs_int32 apart,
		   struct volDescription *volPtr, afs_int32 arraySize)
{
    return vs_ZapVolumeClones(aserver, apart, volPtr, arraySize);
}

int
UV_GenerateVolumeClones(afs_uint32 aserver, afs_int32 apart,
			struct volDescription *volPtr, afs_int32 arraySize)
{
    return vs_GenerateVolumeClones(aserver, apart, volPtr, arraySize);
}

int
UV_ListVolumes(afs_uint32 aserver, afs_int32 apart, int all,
	       struct volintInfo **resultPtr, afs_int32 * size)
{
    return vs_ListVolumes(aserver, apart, all, resultPtr, size);
}

int
UV_XListVolumes(afs_uint32 a_serverID, afs_int32 a_partID, int a_all,
		struct volintXInfo **a_resultPP,
		afs_int32 * a_numEntsInResultP)
{
    return vs_XListVolumes(a_serverID, a_partID, a_all, a_resultPP, a_numEntsInResultP);
}

int
UV_ListOneVolume(afs_uint32 aserver, afs_int32 apart, afs_uint32 volid,
		 struct volintInfo **resultPtr)
{
    return vs_ListOneVolume(aserver, apart, volid,  resultPtr);
}

int
UV_XListOneVolume(afs_uint32 a_serverID, afs_int32 a_partID, afs_uint32 a_volID,
		  struct volintXInfo **a_resultPP)
{
    return vs_XListOneVolume(a_serverID, a_partID, a_volID, a_resultPP);
}

int
UV_SyncVolume(afs_uint32 aserver, afs_int32 apart, char *avolname, int flags)
{
    return vs_SyncVolume(aserver, apart,  avolname, flags);
}

int
UV_SyncVldb(afs_uint32 aserver, afs_int32 apart, int flags, int force)
{
    return vs_SyncVldb(aserver, apart, flags, force);
}

int
UV_SyncServer(afs_uint32 aserver, afs_int32 apart, int flags, int force)
{
    return vs_SyncServer(aserver, apart, flags, force);
}

int
UV_RenameVolume(struct nvldbentry *entry, char oldname[], char newname[])
{
    return vs_RenameVolume(entry, oldname, newname);
}

int
UV_VolserStatus(afs_uint32 server, transDebugInfo ** rpntr, afs_int32 * rcount)
{
    return vs_VolserStatus(server, rpntr, rcount);
}

int
UV_VolumeZap(afs_uint32 server, afs_int32 part, afs_uint32 volid)
{
    return vs_VolumeZap(server, part, volid);
}

int
UV_SetVolume(afs_uint32 server, afs_int32 partition, afs_uint32 volid,
	     afs_int32 transflag, afs_int32 setflag, int sleeptime)
{
    return vs_SetVolume(server, partition, volid, transflag, setflag, sleeptime);
}

int
UV_SetVolumeInfo(afs_uint32 server, afs_int32 partition, afs_uint32 volid,
		 volintInfo * infop)
{
    return vs_SetVolumeInfo(server, partition, volid, infop);
}

int
UV_GetSize(afs_uint32 afromvol, afs_uint32 afromserver, afs_int32 afrompart,
	   afs_int32 fromdate, struct volintSize *vol_size)
{
    return vs_GetSize(afromvol, afromserver, afrompart, fromdate, vol_size);
}
