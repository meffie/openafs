#!/bin/sh
#
# Previously, the openafs-server package stored its configuration,
# database, and log files under the Transarc-style path, /usr/afs.  As of
# the FHS packaging layout, these files live under /etc/openafs/server and
# /var/openafs instead.  This script migrates any files found under the old
# Transarc paths to their new FHS locations.  It is called from the
# openafs-server %post scriptlet on upgrade, and is a no-op on a fresh
# install since there is nothing to migrate.  The openafs-server service
# must be stopped first, since bosserver and the other server processes may
# have the old files open.
#

# Move a file from its old Transarc path to its new FHS path.  The file is
# first renamed to a ".rpmtmp" sibling rather than removed outright, so the
# original data is only discarded after it has been copied successfully to
# the destination.  A leftover ".rpmtmp" file is treated as evidence of a
# previously interrupted migration and stops this script, rather than
# risking silently overwriting or losing data.
_move_file() {
    local from="$1"
    local to="$2"

    if [ ! -e "$from" ]; then
        echo "debug: Skipping '$from'; file does not exist."
        return 0
    fi
    if [ -h "$from" ]; then
        echo "debug: Skipping '$from'; file is a symlink."
        return 0
    fi
    if [ ! -f "$from" ]; then
        echo "debug: Skipping '$from'; not a file."
        return 0
    fi
    if [ -e "$to" ]; then
        echo "error: Unable to move '$from' to '$to'; destination already exists."
        return 1
    fi
    if [ -f "$from.rpmtmp" ]; then
        echo "error: Unable to move '$from' to '$to'; $from.rpmtmp already exists."
        return 1
    fi
    echo "debug: Moving '$from' to '$to'."
    mv "$from" "$from.rpmtmp" && cp "$from.rpmtmp" "$to" && rm "$from.rpmtmp"
    if [ $? -ne 0 ]; then
        echo "error: Failed to move '$from' to '$to'."
        return 1
    fi
}

if /bin/systemctl is-active --quiet openafs-server.service; then
    echo "error: openafs-server is running."
    exit 1
fi

mkdir -p /etc/openafs/server
mkdir -p /var/openafs/backup
mkdir -p /var/openafs/db
mkdir -p /var/log/openafs

_move_file  /usr/afs/backup/tapeconfig        /var/openafs/backup/tapeconfig
_move_file  /usr/afs/db/prdb.DB0              /var/openafs/db/prdb.DB0
_move_file  /usr/afs/db/prdb.DBSYS1           /var/openafs/db/prdb.DBSYS1
_move_file  /usr/afs/db/vldb.DB0              /var/openafs/db/vldb.DB0
_move_file  /usr/afs/db/vldb.DBSYS1           /var/openafs/db/vldb.DBSYS1
_move_file  /usr/afs/etc/CellServDB           /etc/openafs/server/CellServDB
_move_file  /usr/afs/etc/KeyFile              /etc/openafs/server/KeyFile
_move_file  /usr/afs/etc/KeyFileExt           /etc/openafs/server/KeyFileExt
_move_file  /usr/afs/etc/krb.conf             /etc/openafs/server/krb.conf
_move_file  /usr/afs/etc/krb.excl             /etc/openafs/server/krb.excl
_move_file  /usr/afs/etc/openafs-server.conf  /etc/openafs/server/openafs-server.conf
_move_file  /usr/afs/etc/RootVolume           /etc/openafs/server/RootVolume
_move_file  /usr/afs/etc/rxkad.keytab         /etc/openafs/server/rxkad.keytab
_move_file  /usr/afs/etc/ThisCell             /etc/openafs/server/ThisCell
_move_file  /usr/afs/etc/UserList             /etc/openafs/server/UserList
_move_file  /usr/afs/local/Audit              /var/openafs/Audit
_move_file  /usr/afs/local/BosConfig          /etc/openafs/BosConfig
_move_file  /usr/afs/local/BosConfig.new      /etc/openafs/BosConfig.new
_move_file  /usr/afs/local/bosserver.rxbind   /etc/openafs/bosserver.rxbind
_move_file  /usr/afs/local/BozoInit           /etc/openafs/BozoInit
_move_file  /usr/afs/local/fsstate.dat        /var/openafs/fsstate.dat
_move_file  /usr/afs/local/NetInfo            /var/openafs/NetInfo
_move_file  /usr/afs/local/NetRestrict        /var/openafs/NetRestrict
_move_file  /usr/afs/local/NoAuth             /var/openafs/NoAuth
_move_file  /usr/afs/local/salvage.lock       /var/openafs/salvage.lock
_move_file  /usr/afs/local/sysid              /var/openafs/sysid
_move_file  /usr/afs/logs/AuthLog             /var/log/openafs/AuthLog
_move_file  /usr/afs/logs/BackupLog           /var/log/openafs/BackupLog
_move_file  /usr/afs/logs/BosLog              /var/log/openafs/BosLog
_move_file  /usr/afs/logs/FileLog             /var/log/openafs/FileLog
_move_file  /usr/afs/logs/PtLog               /var/log/openafs/PtLog
_move_file  /usr/afs/logs/SalsrvLog           /var/log/openafs/SalsrvLog
_move_file  /usr/afs/logs/SalvageLog          /var/log/openafs/SalvageLog
_move_file  /usr/afs/logs/VLLog               /var/log/openafs/VLLog
_move_file  /usr/afs/logs/VolserLog           /var/log/openafs/VolserLog
