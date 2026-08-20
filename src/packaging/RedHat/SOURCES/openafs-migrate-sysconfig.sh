#!/bin/sh
#
# Previouly, both client and server configurations were in one file,
# /etc/sysconfig/openafs.  This has been split into two files, openafs-client
# and openafs-server, so they can be managed separately. This script migrates
# the settings to the new files if the old file is present.  The original
# /etc/syconfig/openafs file will be removed (or renamed if the settings were
# changed) automatically by rpm.  The openafs-client and openafs-server
# packages will create the configuration files on a fresh installation.
#

if [ -f /etc/sysconfig/openafs ]; then
    # Load current settings.
    . /etc/sysconfig/openafs

    if [ ! -f /etc/sysconfig/openafs-client ]; then
        cat >/etc/sysconfig/openafs-client <<__EOF__
# OpenAFS Client Configuration
AFSD_ARGS="${AFSD_ARGS}"
__EOF__
    fi

    if [ ! -f /etc/sysconfig/openafs-server ]; then
        cat >/etc/sysconfig/openafs-server <<__EOF__
# OpenAFS Server Configuration
BOSSERVER_ARGS="${BOSSERVER_ARGS}"
__EOF__
    fi
fi
