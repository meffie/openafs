#ifndef	_VSUTILS_PROTOTYPES_H
#define _VSUTILS_PROTOTYPES_H
/* vsutils.c */

struct vsu_server_id {
    afs_int32 id;
};
typedef struct vsu_server_id vsu_server_id;

struct vsu_part_id {
    afs_int32 id;
};
typedef struct vsu_part_id vsu_part_id;

struct vsu_site {
    vsu_server_id server;
    vsu_part_id part;
};

extern int VLDB_CreateEntry(struct nvldbentry *entryp);
extern int VLDB_GetEntryByID(afs_uint32 volid, afs_int32 voltype, struct nvldbentry *entryp);
extern int VLDB_GetEntryByName(char *namep, struct nvldbentry *entryp);
extern int VLDB_ReplaceEntry(afs_uint32 volid, afs_int32 voltype, struct nvldbentry *entryp, afs_int32 releasetype);
extern int VLDB_ListAttributes(VldbListByAttributes *attrp, afs_int32 *entriesp, nbulkentries *blkentriesp);
extern int VLDB_ListAttributesN2(VldbListByAttributes *attrp, char *name, afs_int32 thisindex,
           afs_int32 *nentriesp, nbulkentries *blkentriesp, afs_int32 *nextindexp);
extern int VLDB_IsSameAddrs(afs_uint32 serv1, afs_uint32 serv2, afs_int32 *errorp);
extern int vsu_ExtractName(char rname[], char name[]);
extern afs_uint32 vsu_GetVolumeID(char *astring, struct ubik_client *acstruct, afs_int32 *errp);

extern int vsu_GetConnBySite(struct rx_connection **conn, struct nvldbentry *entry,
			     afs_int32 index, afs_int32 voltype);

#endif
