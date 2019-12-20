/*
 * Copyright 2000, International Business Machines Corporation and others.
 * All Rights Reserved.
 *
 * This software has been released under the terms of the IBM Public
 * License.  For details, see the LICENSE file in the top-level source
 * directory or online at http://www.openafs.org/dl/license10.html
 */

#ifndef AFS_VSPROCS_COMPAT_H
#define AFS_VSPROCS_COMPAT_H

/*
 * Compatibility wrappers for libvolser.
 *
 * Note: The following functions are deprecated. Please do not
 *       use them in new programs. They are provided for older
 *       programs which are linked with libvolser.
 */

struct rx_call;
struct rx_connection;
struct rx_securityClass;
struct diskPartition64;
struct nvldbentry;
struct partList;
struct transDebugInfo;
struct volDescription;
struct volintInfo;
struct volintSize;
struct volintXInfo;

int UV_SetSecurity(struct rx_securityClass *as, afs_int32 aindex);

struct rx_connection *UV_Bind(afs_uint32 aserver,
			      afs_int32 port /* note: host order */ );

int UV_NukeVolume(afs_uint32 server, afs_int32 partid, afs_uint32 volid);

int UV_PartitionInfo64(afs_uint32 server, char *pname,
		       struct diskPartition64 *partition);

int UV_CreateVolume(afs_uint32 aserver, afs_int32 apart, char *aname,
		    afs_uint32 * anewid);

int UV_CreateVolume2(afs_uint32 aserver, afs_int32 apart, char *aname,
		     afs_int32 aquota, afs_int32 aspare1, afs_int32 aspare2,
		     afs_int32 aspare3, afs_int32 aspare4,
		     afs_uint32 * anewid);

int UV_CreateVolume3(afs_uint32 aserver, afs_int32 apart, char *aname,
		     afs_int32 aquota, afs_int32 aspare1, afs_int32 aspare2,
		     afs_int32 aspare3, afs_int32 aspare4,
		     afs_uint32 * anewid, afs_uint32 * aroid,
		     afs_uint32 * abkid);

int UV_AddVLDBEntry(afs_uint32 aserver, afs_int32 apart, char *aname,
		    afs_uint32 aid);

int UV_DeleteVolume(afs_uint32 aserver, afs_int32 apart, afs_uint32 avolid);

int UV_ConvertRO(afs_uint32 server, afs_uint32 partition, afs_uint32 volid,
		 struct nvldbentry *entry);

int UV_MoveVolume2(afs_uint32 afromvol, afs_uint32 afromserver,
		   afs_int32 afrompart, afs_uint32 atoserver,
		   afs_int32 atopart, int flags);

int UV_MoveVolume(afs_uint32 afromvol, afs_uint32 afromserver,
		  afs_int32 afrompart, afs_uint32 atoserver,
		  afs_int32 atopart);

int UV_CopyVolume2(afs_uint32 afromvol, afs_uint32 afromserver,
		   afs_int32 afrompart, char *atovolname,
		   afs_uint32 atoserver, afs_int32 atopart,
		   afs_uint32 atovolid, int flags);

int UV_CopyVolume(afs_uint32 afromvol, afs_uint32 afromserver,
		  afs_int32 afrompart, char *atovolname, afs_uint32 atoserver,
		  afs_int32 atopart);

int UV_BackupVolume(afs_uint32 aserver, afs_int32 apart, afs_uint32 avolid);

int UV_CloneVolume(afs_uint32 aserver, afs_int32 apart, afs_uint32 avolid,
		   afs_uint32 acloneid, char *aname, int flags);

int UV_ReleaseVolume(afs_uint32 afromvol, afs_uint32 afromserver,
		     afs_int32 afrompart, int flags);

int UV_DumpVolume(afs_uint32 afromvol, afs_uint32 afromserver,
		  afs_int32 afrompart, afs_int32 fromdate,
		  afs_int32(*DumpFunction) (struct rx_call *, void *),
		  void *rock, afs_int32 flags);

int UV_DumpClonedVolume(afs_uint32 afromvol, afs_uint32 afromserver,
			afs_int32 afrompart, afs_int32 fromdate,
			afs_int32(*DumpFunction) (struct rx_call *, void *),
			void *rock, afs_int32 flags);

int UV_RestoreVolume2(afs_uint32 toserver, afs_int32 topart,
		      afs_uint32 tovolid, afs_uint32 toparentid,
		      char tovolname[], int flags,
		      afs_int32(*WriteData) (struct rx_call *, void *),
		      void *rock);

int UV_RestoreVolume(afs_uint32 toserver, afs_int32 topart,
		     afs_uint32 tovolid, char tovolname[], int flags,
		     afs_int32(*WriteData) (struct rx_call *, void *),
		     void *rock);

int UV_LockRelease(afs_uint32 volid);

int UV_AddSite(afs_uint32 server, afs_int32 part, afs_uint32 volid,
	       afs_int32 valid);

int UV_AddSite2(afs_uint32 server, afs_int32 part, afs_uint32 volid,
		afs_uint32 rovolid, afs_int32 valid);

int UV_RemoveSite(afs_uint32 server, afs_int32 part, afs_uint32 volid);

int UV_ChangeLocation(afs_uint32 server, afs_int32 part, afs_uint32 volid);

int UV_ListPartitions(afs_uint32 aserver, struct partList *ptrPartList,
		      afs_int32 * cntp);

int UV_ZapVolumeClones(afs_uint32 aserver, afs_int32 apart,
		       struct volDescription *volPtr, afs_int32 arraySize);

int UV_GenerateVolumeClones(afs_uint32 aserver, afs_int32 apart,
			    struct volDescription *volPtr,
			    afs_int32 arraySize);

int UV_ListVolumes(afs_uint32 aserver, afs_int32 apart, int all,
		   struct volintInfo **resultPtr, afs_int32 * size);

int UV_XListVolumes(afs_uint32 a_serverID, afs_int32 a_partID, int a_all,
		    struct volintXInfo **a_resultPP,
		    afs_int32 * a_numEntsInResultP);

int UV_ListOneVolume(afs_uint32 aserver, afs_int32 apart, afs_uint32 volid,
		     struct volintInfo **resultPtr);

int UV_XListOneVolume(afs_uint32 a_serverID, afs_int32 a_partID,
		      afs_uint32 a_volID, struct volintXInfo **a_resultPP);

int UV_SyncVolume(afs_uint32 aserver, afs_int32 apart, char *avolname,
		  int flags);

int UV_SyncVldb(afs_uint32 aserver, afs_int32 apart, int flags, int force);

int UV_SyncServer(afs_uint32 aserver, afs_int32 apart, int flags, int force);

int UV_RenameVolume(struct nvldbentry *entry, char oldname[], char newname[]);

int UV_VolserStatus(afs_uint32 server, struct transDebugInfo **rpntr,
		    afs_int32 * rcount);

int UV_VolumeZap(afs_uint32 server, afs_int32 part, afs_uint32 volid);

int UV_SetVolume(afs_uint32 server, afs_int32 partition, afs_uint32 volid,
		 afs_int32 transflag, afs_int32 setflag, int sleeptime);

int UV_SetVolumeInfo(afs_uint32 server, afs_int32 partition, afs_uint32 volid,
		     struct volintInfo *infop);

int UV_GetSize(afs_uint32 afromvol, afs_uint32 afromserver,
	       afs_int32 afrompart, afs_int32 fromdate,
	       struct volintSize *vol_size);

#endif /* AFS_VSPROCS_COMPAT_H */
