#!/bin/sh
#
# Previously, the openafs-client package stored its configuration files
# under the Transarc-style path, /usr/vice/etc.  As of the FHS packaging
# layout, these files live under /etc/openafs instead.  This script
# migrates any configuration files found under the old Transarc path to
# their new FHS location.  It is called from the openafs-client %post
# scriptlet on upgrade, and is a no-op on a fresh install since there is
# nothing to migrate.  The openafs-client service must be stopped first,
# since afsd may have the old files open.
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

if /bin/systemctl is-active --quiet openafs-client.service; then
    echo "error: openafs-client is running."
    exit 1
fi

mkdir -p /etc/openafs

_move_file /usr/vice/etc/CellAlias             /etc/openafs/CellAlias
_move_file /usr/vice/etc/CellServDB            /etc/openafs/CellServDB
_move_file /usr/vice/etc/NetInfo               /etc/openafs/NetInfo
_move_file /usr/vice/etc/NetRestrict           /etc/openafs/NetRestrict
_move_file /usr/vice/etc/openafs-client.conf   /etc/openafs/openafs-client.conf
_move_file /usr/vice/etc/ThisCell              /etc/openafs/ThisCell
