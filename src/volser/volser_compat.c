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

/* called by VLDBClient_Init to set the security module to be used in the RPC */
int
UV_SetSecurity(struct rx_securityClass *as, afs_int32 aindex)
{
    return vs_SetSecurity(as, aindex);
}

/* bind to volser on <port> <aserver> */
/* takes server address in network order, port in host order.  dumb */
struct rx_connection *
UV_Bind(afs_uint32 aserver, afs_int32 port)
{
    struct rx_securityClass *sc = vs_GetSecurityClass();
    afs_int32 index = vs_GetSecurityIndex();

    return rx_NewConnection(aserver, htons(port), VOLSERVICE_ID, sc, index);
}

/* forcibly remove a volume.  Very dangerous call */
int
UV_NukeVolume(afs_uint32 server, afs_int32 partid, afs_uint32 volid)
{
    int code = -1;
    struct rx_connection *tconn;

    tconn = UV_Bind(server, AFSCONF_VOLUMEPORT);
    if (tconn) {
	code = AFSVolNukeVolume(tconn, partid, volid);
	rx_DestroyConnection(tconn);
    }
    return code;
}

int
UV_PartitionInfo64(afs_uint32 server, char *pname,
		   struct diskPartition64 *partition)
{
    int code = -1;
    struct rx_connection *conn;

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
    int code = -1;
    struct rx_connection *conn;
    afs_int32 aquota = 5000;
    afs_uint32 roid = 0;
    afs_uint32 bkid = 0;

    *anewid = 0;
    conn = UV_Bind(aserver, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_CreateVolume(conn, apart, aname, aquota, anewid,
			       &roid, &bkid);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_CreateVolume2(afs_uint32 aserver, afs_int32 apart, char *aname,
		 afs_int32 aquota, afs_int32 aspare1, afs_int32 aspare2,
		 afs_int32 aspare3, afs_int32 aspare4, afs_uint32 * anewid)
{
    int code = -1;
    struct rx_connection *conn;
    afs_uint32 roid = 0;
    afs_uint32 bkid = 0;

    conn = UV_Bind(aserver, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_CreateVolume(conn, apart, aname, aquota, anewid,
			       &roid, &bkid);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_CreateVolume3(afs_uint32 aserver, afs_int32 apart, char *aname,
		 afs_int32 aquota, afs_int32 aspare1, afs_int32 aspare2,
		 afs_int32 aspare3, afs_int32 aspare4, afs_uint32 * anewid,
		 afs_uint32 * aroid, afs_uint32 * abkid)
{
    int code = -1;
    struct rx_connection *conn;

    conn = UV_Bind(aserver, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_CreateVolume(conn, apart, aname, aquota, anewid,
			       aroid, abkid);
	rx_DestroyConnection(conn);
    }
    return code;
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
    int code = -1;
    struct rx_connection *conn;

    conn = UV_Bind(aserver, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_DeleteVolume(conn, aserver, apart, avolid);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_ConvertRO(afs_uint32 server, afs_uint32 partition, afs_uint32 volid,
		struct nvldbentry *entry)
{
    int code = -1;
    struct rx_connection *conn;

    conn = UV_Bind(server, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_ConvertRO(conn, server, partition, volid, entry);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_MoveVolume2(afs_uint32 afromvol, afs_uint32 afromserver, afs_int32 afrompart,
	       afs_uint32 atoserver, afs_int32 atopart, int flags)
{
    int code = -1;
    struct rx_connection *fromconn;
    struct rx_connection *toconn;

    fromconn = UV_Bind(afromserver, AFSCONF_VOLUMEPORT);
    toconn = UV_Bind(atoserver, AFSCONF_VOLUMEPORT);
    if (fromconn && toconn) {
	code = vs_MoveVolume(fromconn, toconn, afromvol, afromserver,
			     afrompart, atoserver, atopart, flags);
    }
    if (fromconn)
	rx_DestroyConnection(fromconn);
    if (toconn)
	rx_DestroyConnection(toconn);
    return code;
}

int
UV_MoveVolume(afs_uint32 afromvol, afs_uint32 afromserver, afs_int32 afrompart,
	      afs_uint32 atoserver, afs_int32 atopart)
{
    int code = -1;
    struct rx_connection *fromconn;
    struct rx_connection *toconn;
    int flags = 0;

    fromconn = UV_Bind(afromserver, AFSCONF_VOLUMEPORT);
    toconn = UV_Bind(atoserver, AFSCONF_VOLUMEPORT);
    if (fromconn && toconn) {
	code = vs_MoveVolume(fromconn, toconn, afromvol, afromserver,
			     afrompart, atoserver, atopart, flags);
    }
    if (fromconn)
	rx_DestroyConnection(fromconn);
    if (toconn)
	rx_DestroyConnection(toconn);
    return code;
}

int
UV_CopyVolume2(afs_uint32 afromvol, afs_uint32 afromserver, afs_int32 afrompart,
	       char *atovolname, afs_uint32 atoserver, afs_int32 atopart,
	       afs_uint32 atovolid, int flags)
{
    int code = -1;
    struct rx_connection *fromconn;
    struct rx_connection *toconn;

    fromconn = UV_Bind(afromserver, AFSCONF_VOLUMEPORT);
    toconn = UV_Bind(atoserver, AFSCONF_VOLUMEPORT);
    if (fromconn && toconn) {
	code = vs_CopyVolume(fromconn, toconn, afromvol,
			     afrompart, atovolname, atoserver, atopart,
			     atovolid, flags);
    }
    if (fromconn)
	rx_DestroyConnection(fromconn);
    if (toconn)
	rx_DestroyConnection(toconn);
    return code;
}

int
UV_CopyVolume(afs_uint32 afromvol, afs_uint32 afromserver, afs_int32 afrompart,
	      char *atovolname, afs_uint32 atoserver, afs_int32 atopart)
{
    int code = -1;
    struct rx_connection *fromconn;
    struct rx_connection *toconn;
    afs_uint32 atovolid = 0;
    int flags = 0;

    fromconn = UV_Bind(afromserver, AFSCONF_VOLUMEPORT);
    toconn = UV_Bind(atoserver, AFSCONF_VOLUMEPORT);
    if (fromconn && toconn) {
	code = vs_CopyVolume(fromconn, toconn, afromvol,
			     afrompart, atovolname, atoserver, atopart,
			     atovolid, flags);
    }
    if (fromconn)
	rx_DestroyConnection(fromconn);
    if (toconn)
	rx_DestroyConnection(toconn);
    return code;
}

int
UV_BackupVolume(afs_uint32 aserver, afs_int32 apart, afs_uint32 avolid)
{
    int code = -1;
    struct rx_connection *conn;

    conn = UV_Bind(aserver, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_BackupVolume(conn, apart, avolid);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_CloneVolume(afs_uint32 aserver, afs_int32 apart, afs_uint32 avolid,
	       afs_uint32 acloneid, char *aname, int flags)
{
    int code = -1;
    struct rx_connection *conn;

    conn = UV_Bind(aserver, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_CloneVolume(conn, apart, avolid, acloneid, aname, flags);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_ReleaseVolume(afs_uint32 afromvol, afs_uint32 afromserver,
		 afs_int32 afrompart, int flags)
{
    int code = -1;
    struct rx_connection *conn;

    conn = UV_Bind(afromserver, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_ReleaseVolume(conn, afromvol, afromserver, afrompart, flags);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_DumpVolume(afs_uint32 afromvol, afs_uint32 afromserver, afs_int32 afrompart,
	      afs_int32 fromdate,
	      afs_int32(*DumpFunction) (struct rx_call *, void *), void *rock,
	      afs_int32 flags)
{
    int code = -1;
    struct rx_connection *conn;

    conn = UV_Bind(afromserver, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_DumpVolume(conn, afromvol, afrompart, fromdate,
			     DumpFunction, rock, flags);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_DumpClonedVolume(afs_uint32 afromvol, afs_uint32 afromserver,
		    afs_int32 afrompart, afs_int32 fromdate,
		    afs_int32(*DumpFunction) (struct rx_call *, void *),
		    void *rock, afs_int32 flags)
{
    int code = -1;
    struct rx_connection *conn;

    conn = UV_Bind(afromserver, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_DumpClonedVolume(conn, afromvol, afrompart, fromdate,
				    DumpFunction, rock, flags);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_RestoreVolume2(afs_uint32 toserver, afs_int32 topart, afs_uint32 tovolid,
		  afs_uint32 toparentid, char tovolname[], int flags,
		  afs_int32(*WriteData) (struct rx_call *, void *),
		  void *rock)
{
    int code = -1;
    struct rx_connection *conn;

    conn = UV_Bind(toserver, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_RestoreVolume(conn, toserver, topart, tovolid, toparentid,
			        tovolname, flags, WriteData, rock);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_RestoreVolume(afs_uint32 toserver, afs_int32 topart, afs_uint32 tovolid,
		 char tovolname[], int flags,
		 afs_int32(*WriteData) (struct rx_call *, void *),
		 void *rock)
{
    int code = -1;
    struct rx_connection *conn;
    afs_uint32 toparentid = 0;

    conn = UV_Bind(toserver, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_RestoreVolume(conn, toserver, topart, tovolid, toparentid,
			        tovolname, flags, WriteData, rock);
	rx_DestroyConnection(conn);
    }
    return code;
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
    int code = -1;
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
    int code = -1;
    struct rx_connection *conn;

    conn = UV_Bind(aserver, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_ZapVolumeClones(conn, apart, volPtr, arraySize);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_GenerateVolumeClones(afs_uint32 aserver, afs_int32 apart,
			struct volDescription *volPtr, afs_int32 arraySize)
{
    int code = -1;
    struct rx_connection *conn;

    conn = UV_Bind(aserver, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_GenerateVolumeClones(conn, apart, volPtr, arraySize);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_ListVolumes(afs_uint32 aserver, afs_int32 apart, int all,
	       struct volintInfo **resultPtr, afs_int32 * size)
{
    int code = -1;
    struct rx_connection *conn;

    conn = UV_Bind(aserver, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_ListVolumes(conn, apart, all, resultPtr, size);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_XListVolumes(afs_uint32 a_serverID, afs_int32 a_partID, int a_all,
		struct volintXInfo **a_resultPP,
		afs_int32 * a_numEntsInResultP)
{
    int code = -1;
    struct rx_connection *conn;

    conn = UV_Bind(a_serverID, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_XListVolumes(conn, a_partID, a_all, a_resultPP, a_numEntsInResultP);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_ListOneVolume(afs_uint32 aserver, afs_int32 apart, afs_uint32 volid,
		 struct volintInfo **resultPtr)
{
    int code = -1;
    struct rx_connection *conn;

    conn = UV_Bind(aserver, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_ListOneVolume(conn, apart, volid,  resultPtr);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_XListOneVolume(afs_uint32 a_serverID, afs_int32 a_partID, afs_uint32 a_volID,
		  struct volintXInfo **a_resultPP)
{
    int code = -1;
    struct rx_connection *conn;

    conn = UV_Bind(a_serverID, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_XListOneVolume(conn, a_partID, a_volID, a_resultPP);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_SyncVolume(afs_uint32 aserver, afs_int32 apart, char *avolname, int flags)
{
    int code = -1;
    struct rx_connection *conn = NULL;

    /* The server id and connection argument is optional for this call. */
    if (aserver) {
	conn = UV_Bind(aserver, AFSCONF_VOLUMEPORT);
    }
    /* should this function be split? one that takes a conn, and one that doesnt? */
    code = vs_SyncVolume(conn, aserver, apart,  avolname, flags);
    if (conn) {
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_SyncVldb(afs_uint32 aserver, afs_int32 apart, int flags, int force)
{
    int code = -1;
    struct rx_connection *conn;

    conn = UV_Bind(aserver, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_SyncVldb(conn, aserver, apart, flags, force);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_SyncServer(afs_uint32 aserver, afs_int32 apart, int flags, int force)
{
    int code = -1;
    struct rx_connection *conn;

    conn = UV_Bind(aserver, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_SyncServer(conn, aserver, apart, flags, force);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_RenameVolume(struct nvldbentry *entry, char oldname[], char newname[])
{
    return vs_RenameVolume(entry, oldname, newname);
}

int
UV_VolserStatus(afs_uint32 server, transDebugInfo ** rpntr, afs_int32 * rcount)
{
    int code = -1;
    struct rx_connection *conn;

    conn = UV_Bind(server, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_VolserStatus(conn, rpntr, rcount);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_VolumeZap(afs_uint32 server, afs_int32 part, afs_uint32 volid)
{
    int code = -1;
    struct rx_connection *conn;

    conn = UV_Bind(server, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_VolumeZap(conn, part, volid);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_SetVolume(afs_uint32 server, afs_int32 partition, afs_uint32 volid,
	     afs_int32 transflag, afs_int32 setflag, int sleeptime)
{
    int code = -1;
    struct rx_connection *conn;

    conn = UV_Bind(server, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_SetVolume(conn, partition, volid, transflag, setflag, sleeptime);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_SetVolumeInfo(afs_uint32 server, afs_int32 partition, afs_uint32 volid,
		 volintInfo * infop)
{
    int code = -1;
    struct rx_connection *conn;

    conn = UV_Bind(server, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_SetVolumeInfo(conn, volid, partition, infop);
	rx_DestroyConnection(conn);
    }
    return code;
}

int
UV_GetSize(afs_uint32 afromvol, afs_uint32 afromserver, afs_int32 afrompart,
	   afs_int32 fromdate, struct volintSize *vol_size)
{
    int code = -1;
    struct rx_connection *conn;

    conn = UV_Bind(afromserver, AFSCONF_VOLUMEPORT);
    if (conn) {
	code = vs_GetSize(conn, afromvol, afrompart, fromdate, vol_size);
	rx_DestroyConnection(conn);
    }
    return code;
}