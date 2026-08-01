#==============================================================================
# OpenAFS spec file for RHEL family distributions
#
# This spec file can be used to build OpenAFS packages for Red Hat Enterprise
# Linux 8 and later (RHEL8+) and compatible distributions.  Downstream packagers are
# encouraged to adapt it to their specific needs.
#
# The following options can be passed to the `rpmbuild` command to customize
# the build process.
#
#   --define "openafs_version <version>"  The version of the OpenAFS source
#                                         archive.
#
#   --define "package_version <version>"  The RPM Version tag.
#                                         (default: openafs_version)
#
#   --define "package_release <release>"  The RPM Release tag.
#                                         (default: 1)
#
#   --define "packager <name>"            The Packager tag.
#                                         (default: OpenAFS Maintainers)
#
#   --define "vendor <name>"              The Vendor tag (default: none)
#
#   --define "source_date_epoch <epoch>"  The build timestamp. (default:
#                                         current system time)
#
#   --define "kernel_version <version>"   The kernel version (including the
#                                         arch suffix) (default: current running kernel)
#
#   --define "kernel_release <release>"   The kernel version (without the arch
#                                         suffix). (default: set from kernel_version)
#
#   --define "kernel_source_dir <path>"   The path to the kernel headers
#                                         and build system (default: autodetect)
#
#   --define "krb5config <path>"          The path to the Kerberos configuration
#                                         (default: none)
#
#   --without userspace                   Do not build userspace packages
#                                         (default: --with userspace)
#
#   --without modules                     Do not the build kernel module package
#                                         (default: --with modules)
#
#   --without dkms                        Do not build the DKMS package
#                                         (default: --with dkms)
#
#   --with supergroups                    Enable supergroup support in the
#                                         Protection Server (ptserver)
#                                         (default: --without supergroup)
#
#==============================================================================

#-----------------------------------------------------------------------------
# Constants
#-----------------------------------------------------------------------------
# Disable link time optimization (lto)
%global _lto_cflags %{nil}

# Disable setting the source_date_epoch from the top entry of the changelog.
%define source_date_epoch_from_changelog 0

# Define the location to the legacy workstation directory.
%global afswsdir /usr/afsws

#-----------------------------------------------------------------------------
# Version information
#-----------------------------------------------------------------------------
%if ! %{defined openafs_version}
%global openafs_version %{nil}
%endif

%if ! %{defined package_version}
%global package_version %{openafs_version}
%endif

%if ! %{defined package_release}
%global package_release 1
%endif

%if ! %{defined packager}
%global packager OpenAFS Maintainers <openafs-bugs@openafs.org>
%endif

%if ! %{defined dkms_version}
%global dkms_version %{package_version}-%{package_release}%{?dist}
%endif

%if ! %{defined source_date_epoch}
%global source_date_epoch %(date +%%s)
%endif

#-----------------------------------------------------------------------------
# Build conditionals
#-----------------------------------------------------------------------------
%bcond_without userspace
%bcond_without modules
%bcond_without dkms
%bcond_with    supergroups

#-----------------------------------------------------------------------------
# Kernel module constants
#-----------------------------------------------------------------------------
%if %{with modules}

%if %{?kernel_version:0}%{!?kernel_version:1}
%if %{?kernvers:1}%{!?kernvers:0}
%{warn: kernvers is deprecated; Use --define "kernel_version <version>"}
%global kernel_version %{kernvers}
%else
%global kernel_version %(uname -r)
%endif
%endif

%global kverrel %(kv="%{kernel_version}"; echo "${kv%.*}")

%if 0%{?amzn} >= 2023
%global kernel_epoch 1:
%else
%global kernel_epoch %nil
%endif

%endif


Summary: OpenAFS distributed filesystem
Name: openafs
Version: %{package_version}
Release: %{package_release}%{?dist}
License: IBM Public License
URL: https://www.openafs.org
BuildRoot: %{_tmppath}/%{name}-%{version}-root
Packager: %{packager}
%if %{?vendor:1}%{!?vendor:0}
Vendor: %{vendor}
%endif
Group: Networking/Filesystems
BuildRequires: %{?kdepend:%{kdepend}, } ncurses-devel, make, flex, bison
BuildRequires: systemd-units
BuildRequires: perl-devel, swig
BuildRequires: perl(ExtUtils::Embed)
BuildRequires: krb5-devel
%if %{with modules}
BuildRequires: kernel-devel
BuildRequires: elfutils-devel
%endif

ExclusiveArch: %{ix86} x86_64 ia64 s390 s390x sparc64 ppc ppc64 ppc64le aarch64

Source0: https://www.openafs.org/dl/openafs/%{openafs_version}/openafs-%{openafs_version}-src.tar.bz2
Source10: https://www.openafs.org/dl/openafs/%{openafs_version}/RELNOTES-%{openafs_version}
Source11: https://www.openafs.org/dl/openafs/%{openafs_version}/ChangeLog
Source20: https://www.central.org/dl/cellservdb/CellServDB.2025-08-16
Source30: openafs-cacheinfo
Source32: openafs-client.service
Source33: openafs-client-systemd-helper.sh
Source34: openafs-LICENSE.Sun
Source35: openafs-README
Source37: openafs-server.service
Source38: openafs.sysconfig
Source39: openafs-ThisCell

%description
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides common files shared across all the various
OpenAFS packages but are not necessarily tied to a client or server.

##############################################################################
#
# build the userspace side of things if so requested
#
##############################################################################
%if %{with userspace}

%package client
Requires: binutils, openafs = %{version}
Requires: systemd-units
Requires(post): systemd-units, systemd-sysv
Requires(preun): systemd-units
Requires(postun): systemd-units

Requires: %{name}-kmod >= %{version}
Provides: %{name}-kmod-common = %{version}

Summary: OpenAFS Filesystem Client
Group: Networking/Filesystem

%description client
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides basic client support to mount and manipulate
AFS.

%package server
Requires: openafs = %{version}
Summary: OpenAFS Filesystem Server
Group: Networking/Filesystems
Requires: systemd-units
Requires(post): systemd-units, systemd-sysv
Requires(preun): systemd-units
Requires(postun): systemd-units

%description server
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides basic server support to host files in an AFS
Cell.

%if %{with dkms}
%package -n dkms-%{name}
Summary:        DKMS-ready kernel source for AFS distributed filesystem
Group:          Development/Kernel
Provides:       openafs-kernel = %{version}
Provides:       %{name}-kmod = %{version}
Requires(pre):  dkms, make, flex
Requires(post): dkms
Requires:       %{name}-kmod-common = %{version}

%description -n dkms-%{name}
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides the source code to allow DKMS to build an
AFS kernel module.
%endif

%package authlibs
Summary: OpenAFS authentication shared libraries
Group: Networking/Filesystems

%description authlibs
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides a shared version of libafsrpc and libafsauthent.
None of the programs included with OpenAFS currently use these shared
libraries; however, third-party software that wishes to perform AFS
authentication may link against them.

%package authlibs-devel
Requires: openafs-authlibs = %{version}-%{release}
Requires: openafs-devel = %{version}-%{release}
Summary: OpenAFS shared library development
Group: Development/Filesystems

%description authlibs-devel
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package includes the static versions of libafsrpc and
libafsauthent, and symlinks required for building against the dynamic
libraries.

%package devel
Summary: OpenAFS Development Libraries and Headers
Group: Development/Filesystems
Requires: openafs = %{version}-%{release}

%description devel
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides static development libraries and headers needed
to compile AFS applications.  Note: AFS currently does not provide
shared libraries.

%package docs
Summary: OpenAFS user and administrator documentation
Requires: openafs = %{version}-%{release}
Group: Networking/Filesystems
BuildRequires: perl-core

%description docs
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides HTML documentation for OpenAFS users and system
administrators.

%package kernel-source
Summary: OpenAFS Kernel Module source tree
Group: Networking/Filesystems
Provides: openafs-kernel = %{version}
Provides: %{name}-kmod = %{version}

%description kernel-source
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides the source code to build your own AFS kernel
module.

%package compat
Summary: OpenAFS client compatibility symlinks
Requires: openafs = %{version}
Group: Networking/Filesystems

%description compat
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides compatibility symlinks in %{afswsdir}.  It is
completely optional, and is only necessary to support legacy
applications and scripts that hard-code the location of AFS client
programs.

%package krb5
Summary: OpenAFS programs to use with krb5
Requires: openafs = %{version}
Group: Networking/Filesystems
BuildRequires: krb5-devel

%description krb5
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides compatibility programs so you can use krb5
to authenticate to AFS services, instead of using AFS's homegrown
krb4 lookalike services.

%endif

##############################################################################
#
# build the kernel modules if so requested
#
##############################################################################
%if %{with modules}

%package -n kmod-%{name}
Summary:          %{name} kernel module
Group:            System Environment/Kernel
Provides:         kernel-modules = %{kernel_epoch}%{kernel_version}
Provides:         %{name}-kmod = %{?epoch:%{epoch}:}%{version}-%{release}
Provides:         openafs-kernel = %{version}
Requires:         kernel-%{_target_cpu} = %{kernel_epoch}%{kverrel}
Requires:         %{name}-kmod-common >= %{?epoch:%{epoch}:}%{version}
Requires(post):   /usr/sbin/depmod
Requires(postun): /usr/sbin/depmod
Release:          %{package_release}.%(echo %{kverrel} | tr - _)
BuildRequires:    kernel-devel-%{_target_cpu} = %{kernel_epoch}%{kverrel}
BuildRequires:    elfutils-devel

%description -n kmod-%{name}
This package provides the %{name} kernel modules built for the Linux
kernel %{kernel_version} for the %{_target_cpu} family of processors.

%endif

##############################################################################
#
# PREP
#
##############################################################################

%prep

: @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
: @@@
: @@@ kernel version:     %{kverrel}
: @@@ build userspace:    %{with userspace}
: @@@ build modules:      %{with modules}
: @@@ arch:               %{_arch}
: @@@ target cpu:         %{_target_cpu}
: @@@
: @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# Install OpenAFS src
%setup -q -n openafs-%{openafs_version}

##############################################################################
#
# building
#
##############################################################################
%build

export SOURCE_DATE_EPOCH=%{source_date_epoch}
export CFLAGS="$RPM_OPT_FLAGS"
%if %{?krb5config:1}%{!?krb5config:0}
export KRB5_CONFIG="%{krb5config}"
%endif

./configure \
       --prefix=%{_prefix} \
       --libdir=%{_libdir} \
       --bindir=%{_bindir} \
       --sbindir=%{_sbindir} \
       --docdir=%{_docdir}/openafs-%{openafs_version} \
       --disable-strip-binaries \
       --enable-debug \
%if %{with modules}
       --with-linux-kernel-packaging \
%if %{?kernel_source_dir:1}%{!?kernel_source_dir:0}
       --with-linux-kernel-headers=%{kernel_source_dir} \
%endif
%else
       --disable-kernel-module \
%endif
       --with-krb5 \
       --with-swig \
       --disable-kauth \
%if %{with supergroups}
       --enable-supergroups \
%endif
       --enable-transarc-paths \
       || exit 1

# Build the libafs tree
make %{_smp_mflags} only_libafs_tree V=0 || exit 1

%if %{?krb5config:1}%{!?krb5config:0}
export KRB5_CONFIG="%{krb5config}"
%endif

%if %{with userspace}
make %{_smp_mflags} all_nolibafs V=0
%endif

%if %{with modules}
make %{_smp_mflags} libafs V=0
%endif

##############################################################################
###
### install
###
##############################################################################
%install

export SOURCE_DATE_EPOCH=%{source_date_epoch}

##############################################################################
###
### Install userspace
###
##############################################################################
%if %{with userspace}

#-----------------------------------------------------------------------------
# Install userspace files
#-----------------------------------------------------------------------------
make %{_smp_mflags} install_nolibafs V=0 DESTDIR="$RPM_BUILD_ROOT"

# Set the executable bit on libraries in libdir, so rpmbuild knows to
# create "Provides" entries in the package metadata for the libraries
chmod +x $RPM_BUILD_ROOT%{_libdir}/*.so*

# Exclude duplicated files.
rm -f $RPM_BUILD_ROOT%{_prefix}/afs/bin/bos
rm -f $RPM_BUILD_ROOT%{_prefix}/afs/bin/fs
rm -f $RPM_BUILD_ROOT%{_prefix}/afs/bin/pts
rm -f $RPM_BUILD_ROOT%{_prefix}/afs/bin/tokens
rm -f $RPM_BUILD_ROOT%{_prefix}/afs/bin/tokens.krb
rm -f $RPM_BUILD_ROOT%{_prefix}/afs/bin/udebug
rm -f $RPM_BUILD_ROOT%{_prefix}/afs/bin/vos

# Relocate afsd to legacy path to match init scripts.
mv $RPM_BUILD_ROOT%{_sbindir}/afsd $RPM_BUILD_ROOT%{_prefix}/vice/etc/afsd

# Relocate admin utilities to a modern path.
mv $RPM_BUILD_ROOT%{_prefix}/afs/bin/prdb_check $RPM_BUILD_ROOT%{_sbindir}/prdb_check
mv $RPM_BUILD_ROOT%{_prefix}/afs/bin/vldb_check $RPM_BUILD_ROOT%{_sbindir}/vldb_check
mv $RPM_BUILD_ROOT%{_prefix}/afs/bin/vldb_convert $RPM_BUILD_ROOT%{_sbindir}/vldb_convert
mv $RPM_BUILD_ROOT%{_prefix}/afs/bin/akeyconvert $RPM_BUILD_ROOT%{_sbindir}/akeyconvert
mv $RPM_BUILD_ROOT%{_prefix}/afs/bin/asetkey $RPM_BUILD_ROOT%{_sbindir}/asetkey

#-----------------------------------------------------------------------------
# Install client and server initscripts/systemd files
#-----------------------------------------------------------------------------
mkdir -p $RPM_BUILD_ROOT/etc/sysconfig
install -m 755 %{SOURCE38} $RPM_BUILD_ROOT/etc/sysconfig/openafs
mkdir -p $RPM_BUILD_ROOT%{_unitdir}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/modules
install -m 644 %{SOURCE32} $RPM_BUILD_ROOT%{_unitdir}/openafs-client.service
install -m 644 %{SOURCE37} $RPM_BUILD_ROOT%{_unitdir}/openafs-server.service
install -m 755 %{SOURCE33} $RPM_BUILD_ROOT%{_prefix}/vice/etc/openafs-client-systemd-helper.sh

#-----------------------------------------------------------------------------
# Install server directories.
#-----------------------------------------------------------------------------
mkdir -p $RPM_BUILD_ROOT%{_prefix}/afs/etc
mkdir -p $RPM_BUILD_ROOT%{_prefix}/afs/logs

#-----------------------------------------------------------------------------
# Install client directories and config files.
#-----------------------------------------------------------------------------
mkdir -p $RPM_BUILD_ROOT%{_prefix}/vice/etc
mkdir -p $RPM_BUILD_ROOT%{_prefix}/vice/cache
chmod 700 $RPM_BUILD_ROOT%{_prefix}/vice/cache
install -p -m 644 %{SOURCE39} $RPM_BUILD_ROOT%{_prefix}/vice/etc/ThisCell
install -p -m 644 %{SOURCE20} $RPM_BUILD_ROOT%{_prefix}/vice/etc/CellServDB.dist
install -p -m 644 %{SOURCE30} $RPM_BUILD_ROOT%{_prefix}/vice/etc/cacheinfo

#-----------------------------------------------------------------------------
# Install DKMS source.
#-----------------------------------------------------------------------------
install -d -m 755 $RPM_BUILD_ROOT%{_prefix}/src
cp -a libafs_tree $RPM_BUILD_ROOT%{_prefix}/src/%{name}-%{dkms_version}

cat > $RPM_BUILD_ROOT%{_prefix}/src/%{name}-%{dkms_version}/dkms.conf <<"EOF"

PACKAGE_VERSION="%{dkms_version}"

# Items below here should not have to change with each driver version.
PACKAGE_NAME="%{name}"
MAKE[0]='./configure --with-linux-kernel-headers=${kernel_source_dir} --with-linux-kernel-packaging && make && mv src/libafs/MODLOAD-*/openafs.ko .'
CLEAN=true

BUILT_MODULE_NAME[0]="$PACKAGE_NAME"
DEST_MODULE_LOCATION[0]="/extra/$PACKAGE_NAME/"
STRIP[0]=no
AUTOINSTALL=yes
NO_WEAK_MODULES=yes

EOF

#-----------------------------------------------------------------------------
# Install the kernel module source tree.
#-----------------------------------------------------------------------------
mkdir -p $RPM_BUILD_ROOT%{_prefix}/src/openafs-kernel-%{openafs_version}/src
tar cf - -C libafs_tree . | \
    tar xf - -C $RPM_BUILD_ROOT%{_prefix}/src/openafs-kernel-%{openafs_version}/src
install -m 644 LICENSE $RPM_BUILD_ROOT%{_prefix}/src/openafs-kernel-%{openafs_version}/LICENSE.IBM
install -m 644 %{SOURCE34} $RPM_BUILD_ROOT%{_prefix}/src/openafs-kernel-%{openafs_version}/LICENSE.Sun
install -m 644 %{SOURCE35} $RPM_BUILD_ROOT%{_prefix}/src/openafs-kernel-%{openafs_version}/README

#-----------------------------------------------------------------------------
# Install documentation.
#-----------------------------------------------------------------------------
mkdir -p $RPM_BUILD_ROOT/$RPM_DOC_DIR/openafs-%{openafs_version}
tar cf - -C doc html pdf | \
    tar xf - -C $RPM_BUILD_ROOT/$RPM_DOC_DIR/openafs-%{openafs_version}
install -m 644 %{SOURCE10} $RPM_BUILD_ROOT/$RPM_DOC_DIR/openafs-%{openafs_version}
install -m 644 %{SOURCE11} $RPM_BUILD_ROOT/$RPM_DOC_DIR/openafs-%{openafs_version}

#-----------------------------------------------------------------------------
# Install directories for compatiblity links.
#-----------------------------------------------------------------------------
mkdir -p $RPM_BUILD_ROOT%{afswsdir}/bin
mkdir -p $RPM_BUILD_ROOT%{afswsdir}/etc

%endif

##############################################################################
###
### Install modules
###
##############################################################################
%if %{with modules}

srcdir=src/libafs/MODLOAD-%{kernel_version}
dstdir=$RPM_BUILD_ROOT/lib/modules/%{kernel_version}/extra/openafs
mkdir -p ${dstdir}
install -m 755 ${srcdir}/openafs.ko ${dstdir}/openafs.ko

%endif


##############################################################################
###
### scripts
###
##############################################################################
%if %{with userspace}

%post client
if [ $1 -eq 1 ] ; then
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi
if [ ! -d /afs ]; then
    mkdir /afs
    chown root:root /afs
    chmod 0755 /afs
    [ -x /sbin/restorecon ] && /sbin/restorecon /afs
fi

# Create the CellServDB
[ -f /usr/vice/etc/CellServDB.local ] || touch /usr/vice/etc/CellServDB.local

( cd /usr/vice/etc ; \
  if [ -h CellServDB ]; then \
    rm -f CellServDB; \
  fi; \
  cat CellServDB.local CellServDB.dist > CellServDB ; \
  chmod 644 CellServDB )

%post server
if [ $1 -eq 1 ] ; then
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%post compat
# Create compatiblity links.
mkdir -p %{afswsdir}/bin
mkdir -p %{afswsdir}/etc
ln -sf %{_bindir}/afsmonitor    %{afswsdir}/bin/afsmonitor
ln -sf %{_bindir}/bos           %{afswsdir}/bin/bos
ln -sf %{_bindir}/fs            %{afswsdir}/bin/fs
ln -sf %{_bindir}/pagsh         %{afswsdir}/bin/pagsh
ln -sf %{_bindir}/pts           %{afswsdir}/bin/pts
ln -sf %{_bindir}/restorevol    %{afswsdir}/bin/restorevol
ln -sf %{_bindir}/scout         %{afswsdir}/bin/scout
ln -sf %{_bindir}/sys           %{afswsdir}/bin/sys
ln -sf %{_bindir}/tokens        %{afswsdir}/bin/tokens
ln -sf %{_bindir}/translate_et  %{afswsdir}/bin/translate_et
ln -sf %{_bindir}/xstat_cm_test %{afswsdir}/bin/xstat_cm_test
ln -sf %{_bindir}/xstat_fs_test %{afswsdir}/bin/xstat_fs_test
ln -sf %{_bindir}/udebug        %{afswsdir}/bin/udebug
ln -sf %{_bindir}/unlog         %{afswsdir}/bin/unlog
ln -sf %{_sbindir}/backup       %{afswsdir}/etc/backup
ln -sf %{_sbindir}/butc         %{afswsdir}/etc/butc
ln -sf %{_sbindir}/fms          %{afswsdir}/etc/fms
ln -sf %{_sbindir}/fstrace      %{afswsdir}/etc/fstrace
ln -sf %{_sbindir}/read_tape    %{afswsdir}/etc/read_tape
ln -sf %{_sbindir}/rxdebug      %{afswsdir}/etc/rxdebug
ln -sf %{_sbindir}/vos          %{afswsdir}/etc/vos
ln -sf %{_sbindir}/vsys         %{afswsdir}/etc/vsys

%post authlibs
/sbin/ldconfig

%postun authlibs
/sbin/ldconfig

%preun
if [ $1 = 0 ] ; then
    [ -d /afs ] && rmdir /afs
    :
fi

%preun client
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable openafs-client.service > /dev/null 2>&1 || :
    /bin/systemctl stop openafs-client.service > /dev/null 2>&1 || :
fi

%preun server
if [ $1 -eq 0 ] ; then
    /bin/systemctl --no-reload disable openafs-server.service > /dev/null 2>&1 || :
    /bin/systemctl stop openafs-server.service > /dev/null 2>&1 || :
fi

%postun client
/bin/systemctl daemon-reload >/dev/null 2>&1 || :

%postun server
/bin/systemctl daemon-reload >/dev/null 2>&1 || :

%if %{with dkms}
%post -n dkms-%{name}
dkms add -m %{name} -v %{dkms_version} --rpm_safe_upgrade
dkms build -m %{name} -v %{dkms_version} --rpm_safe_upgrade
dkms install -m %{name} -v %{dkms_version} --rpm_safe_upgrade

%preun -n dkms-%{name}
dkms remove -m %{name} -v %{dkms_version} --rpm_safe_upgrade --all ||:
%endif
%endif

%triggerun -- openafs-client < 1.6.0-1
# Save the current service runlevel info
# User must manually run systemd-sysv-convert --apply httpd
# to migrate them to systemd targets
/usr/bin/systemd-sysv-convert --save openafs-client >/dev/null 2>&1 ||:

# Run this because the SysV package being removed won't do it
/sbin/chkconfig --del openafs-client >/dev/null 2>&1 || :

%triggerun -- openafs-server < 1.6.0-1
# Save the current service runlevel info
# User must manually run systemd-sysv-convert --apply httpd
# to migrate them to systemd targets
/usr/bin/systemd-sysv-convert --save openafs-server >/dev/null 2>&1 ||:

# Run this because the SysV package being removed won't do it
/sbin/chkconfig --del openafs-server >/dev/null 2>&1 || :

%if %{with module}
%post -n kmod-%{name}
/usr/sbin/depmod -aeF /boot/System.map-%{kernel_version} %{kernel_version} > /dev/null || :

%postun -n kmod-%{name}
/usr/sbin/depmod -aF /boot/System.map-%{kernel_version} %{kernel_version} &> /dev/null || :
%endif

##############################################################################
###
### file lists
###
##############################################################################
%if %{with userspace}

%files
%config(noreplace) /etc/sysconfig/openafs
%doc %{_docdir}/openafs-%{openafs_version}/LICENSE
%{_bindir}/afsmonitor
%{_bindir}/bos
%{_bindir}/fs
%{_bindir}/pagsh
%{_bindir}/pts
%{_bindir}/restorevol
%{_bindir}/scout
%{_bindir}/sys
%{_bindir}/tokens
%{_bindir}/translate_et
%{_bindir}/xstat_cm_test
%{_bindir}/xstat_fs_test
%{_bindir}/udebug
%{_bindir}/unlog
%{_sbindir}/backup
%{_sbindir}/butc
%{_sbindir}/fms
%{_sbindir}/fstrace
%{_sbindir}/read_tape
%{_sbindir}/rxdebug
%{_sbindir}/rxstat_clear_peer
%{_sbindir}/rxstat_clear_process
%{_sbindir}/rxstat_disable_peer
%{_sbindir}/rxstat_disable_process
%{_sbindir}/rxstat_enable_peer
%{_sbindir}/rxstat_enable_process
%{_sbindir}/rxstat_get_peer
%{_sbindir}/rxstat_get_process
%{_sbindir}/rxstat_get_version
%{_sbindir}/rxstat_query_peer
%{_sbindir}/rxstat_query_process
%{_sbindir}/vos
%{_sbindir}/vsys
%{_libdir}/libafshcrypto.so.*
%{_libdir}/librokenafs.so.*
%{_mandir}/man1/afs.1.gz
%{_mandir}/man1/afsmonitor.1.gz
%{_mandir}/man1/fs.1.gz
%{_mandir}/man1/fs_*.1.gz
%{_mandir}/man1/pagsh.1.gz
%{_mandir}/man1/pts.1.gz
%{_mandir}/man1/pts_*.1.gz
%{_mandir}/man1/restorevol.1.gz
%{_mandir}/man1/rxdebug.1.gz
%{_mandir}/man1/scout.1.gz
%{_mandir}/man1/sys.1.gz
%{_mandir}/man1/tokens.1.gz
%{_mandir}/man1/translate_et.1.gz
%{_mandir}/man1/udebug.1.gz
%{_mandir}/man1/unlog.1.gz
%{_mandir}/man1/vos.1.gz
%{_mandir}/man1/vos_*.1.gz
%{_mandir}/man1/xstat_cm_test.1.gz
%{_mandir}/man1/xstat_fs_test.1.gz
%{_mandir}/man5/CellServDB.5.gz
%{_mandir}/man5/ThisCell.5.gz
%{_mandir}/man5/afsmonitor.5.gz
%{_mandir}/man5/butc.5.gz
%{_mandir}/man5/butc_logs.5.gz
%{_mandir}/man8/backup.8.gz
%{_mandir}/man8/backup_*.8.gz
%{_mandir}/man8/bos.8.gz
%{_mandir}/man8/bos_*.8.gz
%{_mandir}/man8/butc.8.gz
%{_mandir}/man8/fms.8.gz
%{_mandir}/man8/fstrace.8.gz
%{_mandir}/man8/fstrace_*.8.gz
%{_mandir}/man8/read_tape.8.gz
# Exclude obsolete or unused files.
%exclude %{_bindir}/livesys
%exclude %{_bindir}/pagsh.krb
%exclude %{_bindir}/tokens.krb
%exclude %{_sbindir}/rmtsysd
%exclude %{_sbindir}/uss
%exclude %{_mandir}/man1/dlog.1.gz
%exclude %{_mandir}/man1/livesys.1.gz
%exclude %{_mandir}/man1/symlink.1.gz
%exclude %{_mandir}/man1/symlink_list.1.gz
%exclude %{_mandir}/man1/symlink_make.1.gz
%exclude %{_mandir}/man1/symlink_remove.1.gz
%exclude %{_mandir}/man5/AuthLog.5.gz
%exclude %{_mandir}/man5/AuthLog.dir.5.gz
%exclude %{_mandir}/man5/uss.5.gz
%exclude %{_mandir}/man5/uss_bulk.5.gz
%exclude %{_mandir}/man8/aklog_dynamic_auth.8.gz
%exclude %{_mandir}/man8/rmtsysd.8.gz
%exclude %{_mandir}/man8/uss.8.gz
%exclude %{_mandir}/man8/uss_*.8.gz
%exclude %{_mandir}/man8/xfs_size_check.8.gz

%files docs
%docdir %{_docdir}/openafs-%{openafs_version}
%dir %{_docdir}/openafs-%{openafs_version}
%{_docdir}/openafs-%{openafs_version}/ChangeLog
%{_docdir}/openafs-%{openafs_version}/RELNOTES-%{openafs_version}
%{_docdir}/openafs-%{openafs_version}/pdf

%files client
%dir %{_prefix}/vice
%dir %{_prefix}/vice/cache
%dir %{_prefix}/vice/etc
%dir %{_prefix}/vice/etc/C
%{_prefix}/vice/etc/CellServDB.dist
%config(noreplace) %{_prefix}/vice/etc/ThisCell
%config(noreplace) %{_prefix}/vice/etc/cacheinfo
%{_bindir}/afsio
%{_bindir}/cmdebug
%{_bindir}/up
%{_prefix}/vice/etc/afsd
%{_prefix}/vice/etc/C/afszcm.cat
%{_libdir}/libuafs.a
%{_libdir}/libuafs_pic.a
%{_unitdir}/openafs-client.service
%{_prefix}/vice/etc/openafs-client-systemd-helper.sh
%{_mandir}/man1/cmdebug.1.gz
%{_mandir}/man1/up.1.gz
%{_mandir}/man5/afs.5.gz
%{_mandir}/man5/afs_cache.5.gz
%{_mandir}/man5/afs_volume_header.5.gz
%{_mandir}/man5/afszcm.cat.5.gz
%{_mandir}/man5/cacheinfo.5.gz
%{_mandir}/man8/afsd.8.gz
%{_mandir}/man8/vsys.8.gz
%{_mandir}/man5/CellAlias.5.gz

%files server
%dir %{_prefix}/afs
%dir %{_prefix}/afs/bin
%dir %{_prefix}/afs/etc
%dir %{_prefix}/afs/logs
%{_prefix}/afs/bin/bosserver
%{_prefix}/afs/bin/bos_util
%{_prefix}/afs/bin/buserver
%{_prefix}/afs/bin/dafileserver
%{_prefix}/afs/bin/dafssync-debug
%{_prefix}/afs/bin/dasalvager
%{_prefix}/afs/bin/davolserver
%{_prefix}/afs/bin/fileserver
%{_prefix}/afs/bin/fssync-debug
%{_prefix}/afs/bin/pt_util
%{_prefix}/afs/bin/ptserver
%{_prefix}/afs/bin/salvager
%{_prefix}/afs/bin/salvageserver
%{_prefix}/afs/bin/salvsync-debug
%{_prefix}/afs/bin/state_analyzer
%{_prefix}/afs/bin/upclient
%{_prefix}/afs/bin/upserver
%{_prefix}/afs/bin/vlserver
%{_prefix}/afs/bin/volinfo
%{_prefix}/afs/bin/volscan
%{_prefix}/afs/bin/volserver
%{_sbindir}/prdb_check
%{_sbindir}/vldb_check
%{_sbindir}/vldb_convert
%{_sbindir}/voldump
%{_unitdir}/openafs-server.service
%{_mandir}/man5/BackupLog.5.gz
%{_mandir}/man5/BosConfig.5.gz
%{_mandir}/man5/BosLog.5.gz
%{_mandir}/man5/FORCESALVAGE.5.gz
%{_mandir}/man5/FileLog.5.gz
%{_mandir}/man5/KeyFile.5.gz
%{_mandir}/man5/KeyFileExt.5.gz
%{_mandir}/man5/NetInfo.5.gz
%{_mandir}/man5/NetRestrict.5.gz
%{_mandir}/man5/NoAuth.5.gz
%{_mandir}/man5/PtLog.5.gz
%{_mandir}/man5/SALVAGE.fs.5.gz
%{_mandir}/man5/SalvageLog.5.gz
%{_mandir}/man5/sysid.5.gz
%{_mandir}/man5/UserList.5.gz
%{_mandir}/man5/VLLog.5.gz
%{_mandir}/man5/VolserLog.5.gz
%{_mandir}/man5/bdb.DB0.5.gz
%{_mandir}/man5/fms.log.5.gz
%{_mandir}/man5/krb.conf.5.gz
%{_mandir}/man5/krb.excl.5.gz
%{_mandir}/man5/prdb.DB0.5.gz
%{_mandir}/man5/salvage.lock.5.gz
%{_mandir}/man5/tapeconfig.5.gz
%{_mandir}/man5/vldb.DB0.5.gz
%{_mandir}/man8/bosserver.8.gz
%{_mandir}/man8/buserver.8.gz
%{_mandir}/man8/fileserver.8.gz
%{_mandir}/man8/dafileserver.8.gz
%{_mandir}/man8/dafssync-debug.8.gz
%{_mandir}/man8/dafssync-debug_*.8.gz
%{_mandir}/man8/dasalvager.8.gz
%{_mandir}/man8/davolserver.8.gz
%{_mandir}/man8/fssync-debug.8.gz
%{_mandir}/man8/fssync-debug_*.8.gz
%{_mandir}/man8/prdb_check.8.gz
%{_mandir}/man8/ptserver.8.gz
%{_mandir}/man8/pt_util.8.gz
%{_mandir}/man8/salvager.8.gz
%{_mandir}/man8/salvageserver.8.gz
%{_mandir}/man8/state_analyzer.8.gz
%{_mandir}/man8/upclient.8.gz
%{_mandir}/man8/upserver.8.gz
%{_mandir}/man8/vldb_check.8.gz
%{_mandir}/man8/vldb_convert.8.gz
%{_mandir}/man8/vlserver.8.gz
%{_mandir}/man8/voldump.8.gz
%{_mandir}/man8/volinfo.8.gz
%{_mandir}/man8/volscan.8.gz
%{_mandir}/man8/volserver.8.gz

%files authlibs
%{_libdir}/libafsauthent.so.*
%{_libdir}/libafsrpc.so.*
%{_libdir}/libkopenafs.so.*

%files authlibs-devel
%{_includedir}/kopenafs.h
%{_libdir}/libafsauthent.a
%{_libdir}/libafscp.a
%{_libdir}/libafsrpc.a
%{_libdir}/libafsauthent_pic.a
%{_libdir}/libafsrpc_pic.a
%{_libdir}/libkopenafs.a
%{_libdir}/libafsauthent.so
%{_libdir}/libafsrpc.so
%{_libdir}/libkopenafs.so

%files devel
%{_bindir}/afs_compile_et
%{_bindir}/rxgen
%{_includedir}/afs
%{_includedir}/lwp.h
%{_includedir}/rx
%{_includedir}/ubik.h
%{_includedir}/ubik_int.h
%{_includedir}/opr/lock.h
%{_includedir}/opr/queue.h
%{_libdir}/afs
%{_libdir}/libafshcrypto.a
%{_libdir}/libafshcrypto.so
%{_libdir}/libafsrfc3961.a
%{_libdir}/liblwp.a
%{_libdir}/libopr.a
%{_libdir}/librokenafs.a
%{_libdir}/librokenafs.so
%{_libdir}/librx.a
%{_libdir}/librxkad.a
%{_libdir}/librxstat.a
%{_libdir}/libubik.a
%{_mandir}/man1/rxgen.1.gz
%{_mandir}/man1/afs_compile_et.1.gz
%{_libdir}/perl/AFS/ukernel.pm
%{_libdir}/perl/ukernel.so
%{_mandir}/man3/AFS::ukernel.3.gz

%if %{with dkms}
%files -n dkms-%{name}
%{_prefix}/src/%{name}-%{dkms_version}
%endif

%files kernel-source
%{_prefix}/src/openafs-kernel-%{openafs_version}/LICENSE.IBM
%{_prefix}/src/openafs-kernel-%{openafs_version}/LICENSE.Sun
%{_prefix}/src/openafs-kernel-%{openafs_version}/README
%{_prefix}/src/openafs-kernel-%{openafs_version}/src

%files compat
%dir %{afswsdir}/bin
%dir %{afswsdir}/etc
%ghost %{afswsdir}/bin/afsmonitor
%ghost %{afswsdir}/bin/bos
%ghost %{afswsdir}/bin/fs
%ghost %{afswsdir}/bin/pagsh
%ghost %{afswsdir}/bin/pts
%ghost %{afswsdir}/bin/restorevol
%ghost %{afswsdir}/bin/scout
%ghost %{afswsdir}/bin/sys
%ghost %{afswsdir}/bin/tokens
%ghost %{afswsdir}/bin/translate_et
%ghost %{afswsdir}/bin/udebug
%ghost %{afswsdir}/bin/unlog
%ghost %{afswsdir}/bin/xstat_cm_test
%ghost %{afswsdir}/bin/xstat_fs_test
%ghost %{afswsdir}/etc/backup
%ghost %{afswsdir}/etc/butc
%ghost %{afswsdir}/etc/fms
%ghost %{afswsdir}/etc/fstrace
%ghost %{afswsdir}/etc/read_tape
%ghost %{afswsdir}/etc/rxdebug
%ghost %{afswsdir}/etc/vos
%ghost %{afswsdir}/etc/vsys

%files krb5
%{_bindir}/aklog
%{_bindir}/klog.krb5
%{_sbindir}/akeyconvert
%{_sbindir}/asetkey
%{_mandir}/man1/aklog.1.gz
%{_mandir}/man1/klog.krb5.1.gz
%{_mandir}/man8/akeyconvert.8.gz
%{_mandir}/man8/asetkey.8.gz

%endif

%if %{with modules}

%files -n kmod-%{name}
/lib/modules/%{kernel_version}/extra/%{name}/

%endif

##############################################################################
###
### openafs.spec change log
###
##############################################################################
%changelog
* Mon Apr 27 2026  Michael Meffie <mmeffie@sinenomine.net>
- Added Amazon Linux support

* Wed Dec 12 2007  Simon Wilkinson <simon@sxw.org.uk> 1.4.5
- Make the RPM mockable

* Mon Oct 29 2007  Simon Wilkinson <simon@sxw.org.uk> 1.4.5
- Update to match the shipped 1.4.5 RPMS
- Fix the kvariant stuff to only configure the 'standard' case once
- Add openafs-kvers.sh back in

* Wed Oct 10 2007  Simon Wilkinson <simon@sxw.org.uk> 1.4.5pre1-1
- Use Fedora style kmods, which allows us to install multiple kernel types

* Thu Jun 07 2007  Simon Wilkinson <simon@sxw.org.uk> 1.4.4-3
- Use distributed files, rather than those in packager's SOURCE directory
- Remove SuidCells stuff, which was unused

* Fri Dec 01 2006  Derrick Brashear <shadow@dementia.org> 1.4.2-2
- integrate s390x changes
- allow for building libafs*.a and not libafs*.so into packages, for platforms
  that won't build the .so files.

* Wed Aug 23 2006  Derrick Brashear <shadow@dementia.org> 1.4.2-1
- update to 1.4.2
- use installed aklog manpage.
- moduleparam patch obsoleted.

* Tue Aug 22 2006  Derek Atkins <warlord@MIT.EDU> 1.4.2-0.1.rc1
- update to 1.4.2-rc1
- hand-apply lee damon's changes to support largesmp kernels from RHEL4
  (but only add support for 2.6 kernels.  No need for the 2.4 kernels).
- don't need the posixlock patch anymore.

* Wed Jul 12 2006  Derek Atkins <warlord@MIT.EDU> 1.4.2-0.beta2
- update to 1.4.2-beta2
- add linux2.4 posixlock API patch

* Mon Jun 26 2006  Derek Atkins <warlord@MIT.EDU>
- moduleparam and krb524 patches no longer required in OA-CVS

* Wed May 17 2006  Derek Atkins <warlord@MIT.EDU>
- change non-target-cpu kernel dep to a file dep
- make sure we use the proper kernel version for the dependency.

* Tue May 16 2006  Derek Atkins <warlord@MIT.EDU>
- allow users to specify local CellServDB and SuidCells entries
  don't overwrite user's changes.  Provide a .dist an let users
  make entries in a ".local"
- build the CellServDB and SuidCells at client startup and at
  client install-time
- add provideskernelarch functionality to openafs-kvers-is.sh
- use that functionality to Require kernel{,-<type>}-targetcpu
  to get better package safety due to RPM bugs where the kernel
  release isn't used so you can install the kernel module against
  any kernel of the same major version.

* Mon May 15 2006  Derek Atkins <warlord@MIT.EDU>
- update the README in openafs-kernel-source
- fix openafs-kvers-is.sh from Alexander Bergolth's patch.
- move kernel module from .../kernel/fs/openafs to .../fs/openafs/

* Fri Apr 21 2006  Derek Atkins <warlord@MIT.EDU>
- build requires autoconf and automake for krb5support
  and autoconf for standard package
- dont setup the krb5 migration kit (or patches) if we don't care.
- require ncurses-devel to build

* Wed Apr 19 2006  Derek Atkins <warlord@MIT.EDU> 1.4.1-3
- look for krb524 functions in libkrb524 if we can't find them
  in the standard locations.

* Tue Apr 18 2006  Derek Atkins <warlord@MIT.EDU> 1.4.1-2
- fix the module_param_array macro for Linux 2.6.9.

* Sat Apr 15 2006  Derek Atkins <warlord@MIT.EDU> 1.4.1-1
- update to 1.4.1 release.
- distribute asetkey from openafs instead of krb5-migration kit
- don't need to apply the FC5 patches because they are part of the distro.
- install asetkey into the "proper" place
- dont list a manpage twice.
- package asetkey man page.  delete it when not needed.

* Thu Apr  6 2006  Derek Atkins <warlord@MIT.EDU>
- turn authlibs back on, because RT #18767 was applied to CVS.

* Wed Mar 29 2006  Derek Atkins <warlord@MIT.EDU> 1.4.1rc10-1
- update to 1.4.1rc10, build on FC5
- fix the man pages (distribute into various packages)
- include patches for FC5, RT #29112 and #29122

* Mon Dec 19 2005  Derek Atkins <warlord@MIT.EDU>
- openafs-server shouldn't depend on the kernel module.

* Thu Nov 17 2005  Derek Atkins <warlord@MIT.EDU>
- patch from Mike Polek <mike at pictage.com> to run depmod for
  the target kernel and not the running kernel.

* Tue Nov  8 2005  Derek Atkins <warlord@MIT.EDU>
- build aklog from the openafs sources, not from the krb5 migration kit.

* Fri Nov  4 2005  Derek Atkins <warlord@MIT.EDU>
- set openafs-kernel-source to Provide openafs-kernel

* Thu Oct 20 2005  Derek Atkins <warlord@MIT.EDU> 1.4.0-1
- update afs-krb5 res_search patch: look for res_search and __res_search
- update to 1.4.0 final

* Mon Oct 10 2005  Derek Atkins <warlord@MIT.EDU>
- remove all kdump builds.

* Thu Oct  6 2005  Derek Atkins <warlord@MIT.EDU>
- fix openafs-kernel-version.sh so it will build an RPM for the
  currently-running kernel even if it's smp on 2.6.

* Tue Sep 27 2005  Derek Atkins <warlord@MIT.EDU> 1.4.0rc5-1
- upgrade to 1.4.0rc5
- turn off authlibs packages

* Fri Sep 23 2005  Derek Atkins <warlord@MIT.EDU> 1.4.0rc4-2
- add kmodule26 patch: fix the kernel module name on 2.6 kernels so
  it's called "openafs" and not "libafs".  This fixes the shutdown
  problem.

* Thu Sep 22 2005  Derek Atkins <warlord@MIT.EDU>
- update kversis script, add 'kvers' operation
- fix bug that 2.6 smp/hugemem kernels don't provide
  kernel-foo = %{kernvers} with 'smp', 'hugemem', etc.
- add patch to remove res_search from the afs-krb5 configure

* Thu Sep 15 2005  Derek Atkins <warlord@MIT.EDU> 1.4.0rc4-1
- Update to 1.4.0rc4
- Update the afs-krb5 krb524 patch so it actually works on
  some older systems like RHEL3 that still need -lkrb524.
- Update the buildall script so choose better architecture support,
  e.g. don't build i586 on RHEL.
- Update the rebuild information in the SPEC file.
- Add support for finding .EL kernels in openafs-kvers-is.sh
- Add additional error messages when kernel version/type parsing fails.
- Update the buildall script to use the kernel srcdir directly.

* Wed Sep 14 2005  Derek Atkins <warlord@MIT.EDU> 1.4.0rc3-2
- Add "hugemem" to 2.4 configs
- Add checks to support scripts to determine whether to build
  the bigmem and/or hugemem kernels for 2.4.

* Mon Sep 12 2005  Derek Atkins <warlord@MIT.EDU> 1.4.0rc3-1
- Added some afs-krb5 patches to get the migration kit to build
  on modern AFS and modern Kerberos.
- Added authlibs and authlibs-devel packages as per UMich changes.

* Sun Sep 11 2005  Derek Atkins <warlord@MIT.EDU>
- Merged in some of the 2.6 changes from wingc@engin.umich.edu

* Sat Sep 10 2005  Derek Atkins <warlord@MIT.EDU>
- Merged in lots of changes from David Howells and Nalin Dahyabhai
  from Red Hat.   Initial attempt at a release of 1.4.  Still need
  to work in a 2.6 build system.
