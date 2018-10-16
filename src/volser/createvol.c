
#include <afsconfig.h>
#include <afs/param.h>

#include <roken.h>

#include <lock.h>
#include <rx/rx_queue.h>
#include <afs/afsint.h>
#include <afs/prs_fs.h>
#include <afs/ihandle.h>
#include <afs/vnode.h>
#include <afs/volume.h>
#include <afs/partition.h>
#include <afs/acl.h>
#include <afs/dir.h>
#include <afs/com_err.h>
#include "vol.h"
#include "physio.h"

int
create_root_vnode(Volume *vp)
{
    DirHandle dir;
    struct acl_accessList *ACL;
    AFSFid did;
    Inode inodeNumber, AFS_UNUSED nearInode;
    struct VnodeDiskObject *vnode;
    struct VnodeClassInfo *vcp = &VnodeClassInfo[vLarge];
    IHandle_t *h;
    FdHandle_t *fdP;
    afs_fsize_t length;
    ssize_t nBytes;

    vnode = calloc(1, SIZEOF_LARGEDISKVNODE);
    if (!vnode)
	return ENOMEM;

    V_pref(vp, nearInode);
    inodeNumber = IH_CREATE(V_linkHandle(vp), V_device(vp),
		  VPartitionPath(V_partition(vp)), nearInode, V_parentId(vp),
		  1, 1, 0);
    if (!VALID_INO(inodeNumber)) {
	/* Log("ViceCreateRoot: IH_CREATE: %s\n", afs_error_message(errno)); */
	free(vnode);
	return EIO;
    }

    SetSalvageDirHandle(&dir, V_parentId(vp), vp->device, inodeNumber);
    did.Volume = V_id(vp);
    did.Vnode = 1;
    did.Unique = 1;

    afs_dir_MakeDir(&dir, (afs_int32 *)&did, (afs_int32 *)&did);
    DFlush();			/* flush all modified dir buffers out */
    DZap(&dir);			/* Remove all buffers for this dir */
    length = afs_dir_Length(&dir);	/* Remember size of this directory */

    FidZap(&dir);		/* Done with the dir handle obtained via SetSalvageDirHandle() */

    /* build a single entry ACL that gives all rights to system:administrators */
    /* this section of code assumes that access list format is not going to
     * change
     */
    ACL = VVnodeDiskACL(vnode);
    ACL->size = sizeof(struct acl_accessList);
    ACL->version = ACL_ACLVERSION;
    ACL->total = 1;
    ACL->positive = 1;
    ACL->negative = 0;
    ACL->entries[0].id = -204;	/* this assumes System:administrators is group -204 */
    ACL->entries[0].rights =
	PRSFS_READ | PRSFS_WRITE | PRSFS_INSERT | PRSFS_LOOKUP | PRSFS_DELETE
	| PRSFS_LOCK | PRSFS_ADMINISTER;

    vnode->type = vDirectory;
    vnode->cloned = 0;
    vnode->modeBits = 0777;
    vnode->linkCount = 2;
    VNDISK_SET_LEN(vnode, length);
    vnode->uniquifier = 1;
    V_uniquifier(vp) = vnode->uniquifier + 1;
    vnode->dataVersion = 1;
    VNDISK_SET_INO(vnode, inodeNumber);
    vnode->unixModifyTime = vnode->serverModifyTime = V_creationDate(vp);
    vnode->author = 0;
    vnode->owner = 0;
    vnode->parent = 0;
    vnode->vnodeMagic = vcp->magic;

    IH_INIT(h, vp->device, V_parentId(vp), vp->vnodeIndex[vLarge].handle->ih_ino);
    fdP = IH_OPEN(h);
    if (fdP == NULL) {
	return -1;
    }
    nBytes = FDH_PWRITE(fdP, vnode, SIZEOF_LARGEDISKVNODE, vnodeIndexOffset(vcp, 1));
    if (nBytes != SIZEOF_LARGEDISKVNODE) {
	return -1;
    }
    FDH_REALLYCLOSE(fdP);
    IH_RELEASE(h);
    VNDISK_GET_LEN(length, vnode);
    V_diskused(vp) = nBlocks(length);

    free(vnode);
    return 0;
}

int
create_volume(void)
{
    Volume *vp;
    Error error;
    char *path = "/vicepa";
    VolumeId volume_id = 123456;
    VolumeId parent_id = volume_id;
    afs_int32 atype = readwriteVolume;
    char *name = "xyzzy";

    vp = VCreateVolume(&error, path, volume_id, parent_id);
    if (error) {
        fprintf(stderr, "Failed to create volume; error=%d\n", error);
        return -1;
    }

    V_destroyMe(vp) = DESTROY_ME;
    V_uniquifier(vp) = 1;
    V_updateDate(vp) = V_creationDate(vp) = V_copyDate(vp);
    V_inService(vp) = V_blessed(vp) = 1;
    V_type(vp) = atype;
    AssignVolumeName(&V_disk(vp), name, 0);

    error = create_root_vnode(vp);
    if (error) {
        return -1;
    }

    V_destroyMe(vp) = 0;
    V_inService(vp) = 1;
    V_maxquota(vp) = 5000;
    VUpdateVolume(&error, vp);
    if (error) {
        fprintf(stderr, "Failed to update volume.\n");
    }

    return 0;
}

int
main(int argc, char *argv[])
{
    int code;
    VolumePackageOptions opts;

    VOptDefaults(volumeUtility, &opts);
    if (VInitVolumePackage2(volumeUtility, &opts)) {
        fprintf(stderr, "Failed to initialize.\n");
        return -1;
    }

    DInit(10);
    code = VAttachPartitions();
    if (code) {
        fprintf(stderr, "Failed to attach partitions.\n");
        return -1;
    }

    code = create_volume();
    return code;
}
