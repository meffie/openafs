#!/bin/sh
#
# Register SELinux file contexts and policy for the openafs-server FHS
# paths, and relabel any files already on disk.
#
# RHEL-family selinux-policy-targeted ships a legacy "afs" module written
# for the classic Transarc-style paths (/usr/afs/bin/fileserver, etc).
# Some of the openafs-server binaries and data paths match that module's
# patterns by coincidence (e.g. /usr/libexec/openafs/fileserver), while
# others (the demand-attach binaries, /var/openafs) do not match anything
# and are left unlabeled, or worse, pulled into a confined domain without
# the matching data directories to go with it. This script adds local
# fcontext equivalents mapping our FHS paths onto the module's existing
# types, loads the small policy supplement in openafs-selinux.cil that
# covers the one real gap in that module (demand-attach fileserver IPC
# sockets), and relabels the paths that already exist.
#
# This is a no-op when SELinux is disabled, or when the SELinux userspace
# tools (policycoreutils-python-utils) are not installed.  It is called
# from the openafs-server %post and %postun scriptlets.
#
# usage: openafs-selinux-relabel.sh <install|remove> <path-to-cil-module>

action="$1"
cil_module="$2"

if ! /usr/sbin/selinuxenabled 2>/dev/null; then
    exit 0
fi
if [ ! -x /usr/sbin/semanage ] || [ ! -x /usr/sbin/semodule ]; then
    echo "debug: semanage/semodule not found; skipping SELinux setup."
    exit 0
fi

# path type
_fcontexts="
/usr/libexec/openafs/dafileserver	afs_fsserver_exec_t
/usr/libexec/openafs/dasalvager	afs_fsserver_exec_t
/usr/libexec/openafs/davolserver	afs_fsserver_exec_t
/usr/libexec/openafs/salvageserver	afs_fsserver_exec_t
/var/openafs(/.*)?			afs_config_t
/var/openafs/db(/.*)?			afs_dbdir_t
/var/openafs/db/prdb\..*		afs_pt_db_t
/var/openafs/db/vldb\..*		afs_vl_db_t
/var/log/openafs(/.*)?			afs_logfile_t
/vicep[a-z][a-z]?(/.*)?		afs_files_t
"

case "$action" in
install)
    echo "$_fcontexts" | while read -r path type; do
        [ -n "$path" ] || continue
        /usr/sbin/semanage fcontext -a -t "$type" "$path" 2>/dev/null || :
    done
    /usr/sbin/semodule -i "$cil_module" || :
    /sbin/restorecon -R \
        /usr/libexec/openafs /usr/sbin/bosserver \
        /etc/openafs /var/openafs /var/log/openafs /vicep* \
        >/dev/null 2>&1 || :
    ;;
remove)
    echo "$_fcontexts" | while read -r path type; do
        [ -n "$path" ] || continue
        /usr/sbin/semanage fcontext -d "$path" 2>/dev/null || :
    done
    /usr/sbin/semodule -r openafs-selinux >/dev/null 2>&1 || :
    ;;
*)
    echo "error: unknown action '$action'." >&2
    exit 1
    ;;
esac
