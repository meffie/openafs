#-----------------------------------------------------------------------------
# OpenAFS spec file for RHEL and compatible distributions
#
# This spec file is used to build OpenAFS RPMs for Red Hat Enterprise Linux
# (RHEL), and RHEL-compatible distributions such as Fedora, CentOS Stream,
# AlmaLinux, Rocky Linux, Oracle Linux, and Amazon Linux.
#
#-----------------------------------------------------------------------------

%define afsvers @PACKAGE_VERSION@
%define pkgvers @LINUX_PKGVER@
# for beta/rc releases make pkgrel 0.<tag>
# for real releases make pkgrel 1 (or more for extra releases)
%define pkgrel @LINUX_PKGREL@

# Disable using lto (link time optimization)
%global _lto_cflags %{nil}

# Define the location to the legacy workstation directory.
%global afswsdir /usr/afsws

#
# Disable setting the source_date_epoch from the top entry of the changelog and
# instead use the current system time by default.
#
# Note: Downstream packagers which use this reference spec are encouraged
#       to set source_date_epoch_from_changelog to 1 and update the changelog
#       on each release to set the source_date_epoch.
#
%define source_date_epoch_from_changelog 0
%{!?source_date_epoch: %global source_date_epoch %(date +%%s)}

%{!?build_dkmspkg: %define build_dkmspkg 1}

#
# Determine presence of rpmbuild command line --define arguments and set
# defaults if not present.
#
%define build_userspace_on_cmdline %{?build_userspace:1}%{!?build_userspace:0}
%define build_modules_on_cmdline %{?build_modules:1}%{!?build_modules:0}

%if !%{build_userspace_on_cmdline}
%define build_userspace 1
%endif
%if !%{build_modules_on_cmdline}
%define build_modules 1
%endif

# Specify '--with kauth' if you want to build packages containing the legacy
# kaserver and related programs.
%define kauth_support %{?_with_kauth:1}%{!?_with_kauth:0}

# Specify '--without authlibs' if you do not want to build the openafs-authlibs
# package.
%define build_authlibs %{?_without_authlibs:0}%{!?_without_authlibs:1}

# Specify '--without krb5' if you do not want to build the openafs-krb5 package
# to distribute aklog, asetkey, and akeyconvert.
%define krb5support %{?_without_krb5:0}%{!?_without_krb5:1}

%if %{?kernvers:0}%{!?kernvers:1}
%global kernvers %(uname -r)
%endif

%global kverrel %(echo %{kernvers} | sed 's/\.%{_target_cpu}$//')

# The kernel modules installation path.
%if ! %{defined kmodulesdir}
%global kmodulesdir %{_prefix}/lib/modules/%{kernvers}
%endif

# The path to the kernel headers for the target kernel version.
%if ! %{defined ksrcdir}
%global ksrcdir %{_usrsrc}/kernels/%{kernvers}
%endif

%if 0%{?amzn} >= 2023
%global kernel_epoch 1:
%else
%global kernel_epoch %nil
%endif

%define dkms_version %{pkgvers}-%{pkgrel}%{?dist}

# Define the location of the PAM security module directory
%define pamdir /%{_lib}/security

Summary: OpenAFS distributed filesystem
Name: openafs
Version: %{pkgvers}
Release: %{pkgrel}%{?dist}
License: IBM Public License
URL: https://www.openafs.org
Group: Networking/Filesystems
BuildRequires: pam-devel, ncurses-devel, make, flex, bison
BuildRequires: systemd-units
BuildRequires: perl-devel, swig
BuildRequires: perl(ExtUtils::Embed)
%if %{krb5support}
BuildRequires: krb5-devel
%endif
%if %{build_modules}
BuildRequires: kernel-devel
BuildRequires: elfutils-devel
%endif

ExclusiveArch: %{ix86} x86_64 ia64 s390 s390x sparc64 ppc ppc64 ppc64le aarch64

Source0: https://www.openafs.org/dl/openafs/%{afsvers}/openafs-%{afsvers}-src.tar.bz2
%define srcdir openafs-%{afsvers}
Source10: https://www.openafs.org/dl/openafs/%{afsvers}/RELNOTES-%{afsvers}
Source11: https://www.openafs.org/dl/openafs/%{afsvers}/ChangeLog
Source20: https://www.central.org/dl/cellservdb/CellServDB.2025-08-16
Source21: openafs-CellServDB.local
Source30: openafs-cacheinfo
Source32: openafs-client.service
Source33: openafs-client-systemd-helper.sh
Source34: openafs-LICENSE.Sun
Source35: openafs-README
Source37: openafs-server.service
Source38: openafs.sysconfig
Source39: openafs-ThisCell
Source40: openafs-dkms.conf

%description
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides common files shared across all the various
OpenAFS packages but are not necessarily tied to a client or server.

The OpenAFS SRPM can be rebuilt with the following options:

 --define "source_date_epoch 1712832000"  Specify the build timestamp. The default
                                          is the current system time.

 --define "kernvers 3.19.3-100.fc20.i686" Specify the specific kernel version
                                  to build modules against. The default is
                                  to build against the currently-running
                                  kernel.

 --without authlibs               Disable authlibs package (default: with authlibs)
 --without krb5                   Disable krb5 support (default: with krb5)
 --with bitmap-later              Enable "bitmap later" support
 --with supergroups               Enable "supergroups"
 --with kauth                     Build the openafs-kauth-server and openafs-kauth-client
                                  packages which contain the legacy kaserver and
                                  related programs. (default: --without kauth)

 --target=i386                    The target architecture to build for.

 --define "build_userspace 1"     Request building of userspace tools
 --define "build_modules 1"       Request building of kernel modules
                                  You probably never need to specify these.

 --define "kmodulesdir <path>"    This is the base location where modules
                                  will be installed.  You probably don't
                                  need to change this ever.

To a kernel module for your running kernel, just run:
  rpmbuild --rebuild --target=`uname -m` openafs-%{pkgvers}-%{pkgrel}%{?dist}.src.rpm

%if %{build_userspace}

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

%if %{build_dkmspkg}
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

%if %{build_authlibs}
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
%endif

%package authlibs-devel
%if %{build_authlibs}
Requires: openafs-authlibs = %{version}-%{release}
%endif
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

%if %{kauth_support}
%package kauth-client
Summary: OpenAFS Kauth Client support
Requires: openafs
Group: Networking/Filesystems

%description kauth-client
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides the legacy KAServer client programs and the PAM module
for authentication with the OpenAFS KAserver; a deprecated authentication
service.  Generally you should not install this package for new cells or for
cells using Kerberos v5.

%package kauth-server
Summary: OpenAFS Kauth Server support
Requires: openafs
Group: Networking/Filesystems

%description kauth-server
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides the legacy OpenAFS KAServer; a deprecated authentication
service. Generally you should not install this package for new cells or for
cells using Kerberos v5.
%endif

%if %{krb5support}
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

%endif

%if %{build_modules}

%package -n kmod-%{name}
Summary:          %{name} kernel module
Group:            System Environment/Kernel
Provides:         %{name}-kmod = %{?epoch:%{epoch}:}%{version}-%{release}
Provides:         openafs-kernel = %{version}
Requires:         kernel-%{_target_cpu} = %{kernel_epoch}%{kverrel}
Requires:         %{name}-kmod-common >= %{?epoch:%{epoch}:}%{version}
Requires(post):   /usr/sbin/depmod
Requires(postun): /usr/sbin/depmod
Release:          %{pkgrel}.%(echo %{kverrel} | tr - _)
BuildRequires:    kernel-devel-%{_target_cpu} = %{kernel_epoch}%{kverrel}
BuildRequires:    elfutils-devel

%description -n kmod-%{name}
This package provides the %{name} kernel modules built for the Linux
kernel %{kernvers}.

%endif

#-----------------------------------------------------------------------------
# Preparation stage
#-----------------------------------------------------------------------------
%prep

: @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
: @@@
: @@@ kernel version:     %{kverrel}
: @@@ PAM modules dir:    %{pamdir}
: @@@ build userspace:    %{build_userspace}
: @@@ build modules:      %{build_modules}
: @@@ arch:               %{_arch}
: @@@ target cpu:         %{_target_cpu}
: @@@
: @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

%setup -q -n %{srcdir}

# Add the change log and release notes to source tree.
cp -p %{SOURCE10} .
cp -p %{SOURCE11} .

#-----------------------------------------------------------------------------
# Build stage
#-----------------------------------------------------------------------------
%build

export SOURCE_DATE_EPOCH=%{source_date_epoch}
%set_build_flags

./configure \
       --prefix=%{_prefix} \
       --libdir=%{_libdir} \
       --bindir=%{_bindir} \
       --sbindir=%{_sbindir} \
       --disable-strip-binaries \
       --enable-debug \
       --with-linux-kernel-packaging \
%if %{build_modules}
       --enable-kernel-module \
       --with-linux-kernel-headers=%{ksrcdir} \
%else
       --disable-kernel-module \
%endif
%if %{krb5support}
       --with-krb5 \
%endif
       --with-swig \
%if %{kauth_support}
       --enable-kauth \
%endif
%if 0%{?_with_supergroups}
       --enable-supergroups \
%endif
       --enable-transarc-paths

%if %{build_userspace} && %{build_modules}
TARGET=all
%elif %{build_userspace}
TARGET=all_nolibafs
%elif %{build_modules}
TARGET=libafs
%else
%{error:At least one of build_userspace or build_modules must be enabled.}
%endif

%make_build only_libafs_tree $TARGET V=0

#-----------------------------------------------------------------------------
# Install stage
#-----------------------------------------------------------------------------
%install

export SOURCE_DATE_EPOCH=%{source_date_epoch}

%if %{build_userspace}

# Install userspace files
make %{_smp_mflags} install_nolibafs DESTDIR="%{buildroot}"

# Exclude duplicated files.
rm -f %{buildroot}%{_prefix}/afs/bin/bos
rm -f %{buildroot}%{_prefix}/afs/bin/fs
%if %{kauth_support}
rm -f %{buildroot}%{_prefix}/afs/bin/kas
rm -f %{buildroot}%{_prefix}/afs/bin/klog
rm -f %{buildroot}%{_prefix}/afs/bin/klog.krb
rm -f %{buildroot}%{_prefix}/afs/bin/kpwvalid
rm -f %{buildroot}%{_sbindir}/kpwvalid
%endif
rm -f %{buildroot}%{_prefix}/afs/bin/pts
rm -f %{buildroot}%{_prefix}/afs/bin/tokens
rm -f %{buildroot}%{_prefix}/afs/bin/tokens.krb
rm -f %{buildroot}%{_prefix}/afs/bin/udebug
rm -f %{buildroot}%{_prefix}/afs/bin/vos

# Relocate afsd to legacy path to match systemd files.
mv %{buildroot}%{_sbindir}/afsd %{buildroot}%{_prefix}/vice/etc/afsd

# Relocate admin utilities to a modern path.
%if %{kauth_support}
mv %{buildroot}%{_prefix}/afs/bin/kadb_check %{buildroot}%{_sbindir}/kadb_check
%endif
mv %{buildroot}%{_prefix}/afs/bin/prdb_check %{buildroot}%{_sbindir}/prdb_check
mv %{buildroot}%{_prefix}/afs/bin/vldb_check %{buildroot}%{_sbindir}/vldb_check
mv %{buildroot}%{_prefix}/afs/bin/vldb_convert %{buildroot}%{_sbindir}/vldb_convert
%if %{krb5support}
mv %{buildroot}%{_prefix}/afs/bin/akeyconvert %{buildroot}%{_sbindir}/akeyconvert
mv %{buildroot}%{_prefix}/afs/bin/asetkey %{buildroot}%{_sbindir}/asetkey
%endif

%if %{kauth_support}
# Relocate PAM files to the standard PAM module path.
mkdir -p %{buildroot}%{pamdir}
mv %{buildroot}%{_libdir}/pam_afs.krb.so %{buildroot}%{pamdir}
mv %{buildroot}%{_libdir}/pam_afs.so %{buildroot}%{pamdir}
ln -sf pam_afs.so %{buildroot}%{pamdir}/pam_afs.so.1
ln -sf pam_afs.krb.so %{buildroot}%{pamdir}/pam_afs.krb.so.1

# Rename kpasswd to avoid conflicting with krb5 kpasswd.
mv %{buildroot}%{_bindir}/kpasswd %{buildroot}%{_bindir}/kapasswd
mv %{buildroot}%{_mandir}/man1/kpasswd.1 %{buildroot}%{_mandir}/man1/kapasswd.1
%endif


# Install client and server systemd files.
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
install -m 755 %{SOURCE38} %{buildroot}%{_sysconfdir}/sysconfig/openafs
mkdir -p %{buildroot}%{_unitdir}
install -m 644 %{SOURCE32} %{buildroot}%{_unitdir}/openafs-client.service
install -m 644 %{SOURCE37} %{buildroot}%{_unitdir}/openafs-server.service
install -m 755 %{SOURCE33} %{buildroot}%{_prefix}/vice/etc/openafs-client-systemd-helper.sh

# Install server directories.
mkdir -p %{buildroot}%{_prefix}/afs/etc
mkdir -p %{buildroot}%{_prefix}/afs/logs

# Install client directories and config files.
mkdir -p %{buildroot}%{_prefix}/vice/etc
mkdir -p %{buildroot}%{_prefix}/vice/cache
chmod 700 %{buildroot}%{_prefix}/vice/cache
install -p -m 644 %{SOURCE39} %{buildroot}%{_prefix}/vice/etc/ThisCell
install -p -m 644 %{SOURCE20} %{buildroot}%{_prefix}/vice/etc/CellServDB.dist
install -p -m 644 %{SOURCE21} %{buildroot}%{_prefix}/vice/etc/CellServDB.local
install -p -m 644 %{SOURCE30} %{buildroot}%{_prefix}/vice/etc/cacheinfo

# Install DKMS source.
install -d -m 755 %{buildroot}%{_prefix}/src
cp -a libafs_tree %{buildroot}%{_prefix}/src/%{name}-%{dkms_version}
sed -e 's/@NAME@/%{name}/' \
    -e 's/@PACKAGE_VERSION@/%{dkms_version}/' \
    %{SOURCE40} > %{buildroot}%{_prefix}/src/%{name}-%{dkms_version}/dkms.conf

# Install the kernel module source tree.
mkdir -p %{buildroot}%{_prefix}/src/openafs-kernel-%{afsvers}/src
tar cf - -C libafs_tree . | \
    tar xf - -C %{buildroot}%{_prefix}/src/openafs-kernel-%{afsvers}/src
install -m 644 LICENSE %{buildroot}%{_prefix}/src/openafs-kernel-%{afsvers}/LICENSE.IBM
install -m 644 %{SOURCE34} %{buildroot}%{_prefix}/src/openafs-kernel-%{afsvers}/LICENSE.Sun
install -m 644 %{SOURCE35} %{buildroot}%{_prefix}/src/openafs-kernel-%{afsvers}/README

%endif

# Install kernel modules
%if %{build_modules}

mkdir -p %{buildroot}%{kmodulesdir}/extra/%{name}
install -m 755 \
    src/libafs/MODLOAD-%{kernvers}/openafs.ko \
    %{buildroot}%{kmodulesdir}/extra/%{name}/%{name}.ko

%endif

#-----------------------------------------------------------------------------
# Check stage
#-----------------------------------------------------------------------------
%check
%if %{build_userspace}
make check
%endif

#-----------------------------------------------------------------------------
# Scriptlets
#-----------------------------------------------------------------------------
%if %{build_userspace}

# openafs scriptlets
%preun
if [ $1 = 0 ] ; then
    if [ -d /afs ]; then
        rmdir /afs || :
    fi
fi

# openafs-client scriptlets
%post client
if [ ! -d /afs ]; then
    mkdir /afs
    chown root:root /afs
    chmod 0555 /afs
    [ -x /sbin/restorecon ] && /sbin/restorecon /afs
fi
%systemd_post openafs-client.service

%preun client
%systemd_preun openafs-client.service

%postun client
%systemd_postun openafs-client.service

# openafs-server scriptlets
%post server
%systemd_post openafs-server.service

%preun server
%systemd_preun openafs-server.service

%postun server
%systemd_postun openafs-server.service

# openafs-comp scriptlets
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
%if %{kauth_support}
ln -sf %{_sbindir}/uss          %{afswsdir}/etc/uss
%endif
ln -sf %{_sbindir}/vos          %{afswsdir}/etc/vos
ln -sf %{_sbindir}/vsys         %{afswsdir}/etc/vsys

%postun compat
if [ $1 = 0 ] ; then
    rmdir %{afswsdir}/bin >/dev/null 2>/dev/null || :
    rmdir %{afswsdir}/etc >/dev/null 2>/dev/null || :
    rmdir %{afswsdir} >/dev/null 2>/dev/null || :
fi

# openafs-kauth-client scriptlets
%if %{kauth_support}
%post kauth-client
# Create compatiblity links.
mkdir -p %{afswsdir}/bin
mkdir -p %{afswsdir}/etc
ln -sf %{_bindir}/kapasswd      %{afswsdir}/bin/kapasswd
ln -sf %{_bindir}/klog          %{afswsdir}/bin/klog
ln -sf %{_bindir}/klog.krb      %{afswsdir}/bin/klog.krb
ln -sf %{_sbindir}/kas          %{afswsdir}/etc/kas
ln -sf %{_bindir}/pagsh.krb     %{afswsdir}/bin/pagsh.krb
ln -sf %{_bindir}/tokens.krb    %{afswsdir}/bin/tokens.krb

%postun kauth-client
if [ $1 = 0 ] ; then
    rmdir %{afswsdir}/bin >/dev/null 2>/dev/null || :
    rmdir %{afswsdir}/etc >/dev/null 2>/dev/null || :
    rmdir %{afswsdir} >/dev/null 2>/dev/null || :
fi
%endif

# dkms-openafs scriptlets
%if %{build_dkmspkg}
%post -n dkms-%{name}
dkms add -m %{name} -v %{dkms_version} --rpm_safe_upgrade
dkms build -m %{name} -v %{dkms_version} --rpm_safe_upgrade
dkms install -m %{name} -v %{dkms_version} --rpm_safe_upgrade

%preun -n dkms-%{name}
dkms remove -m %{name} -v %{dkms_version} --rpm_safe_upgrade --all ||:
%endif
%endif

# kmod-openafs scriptlets
%if %{build_modules}
%post -n kmod-%{name}
/usr/sbin/depmod -aeF /boot/System.map-%{kernvers} %{kernvers} > /dev/null || :

%postun -n kmod-%{name}
/usr/sbin/depmod -aF /boot/System.map-%{kernvers} %{kernvers} &> /dev/null || :
%endif

#-----------------------------------------------------------------------------
# File lists
#-----------------------------------------------------------------------------
%if %{build_userspace}

%files
%config(noreplace) %{_sysconfdir}/sysconfig/openafs
%doc LICENSE
%doc ChangeLog
%doc RELNOTES-%{afsvers}
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
%if %{kauth_support}
%{_sbindir}/uss
%endif
%{_sbindir}/vos
%{_sbindir}/vsys
%{_libdir}/libafshcrypto.so.*
%{_libdir}/librokenafs.so.*
%doc %{_mandir}/man1/afs.1.*
%doc %{_mandir}/man1/afsmonitor.1.*
%doc %{_mandir}/man1/fs.1.*
%doc %{_mandir}/man1/fs_*.1.*
%doc %{_mandir}/man1/pagsh.1.*
%doc %{_mandir}/man1/pts.1.*
%doc %{_mandir}/man1/pts_*.1.*
%doc %{_mandir}/man1/restorevol.1.*
%doc %{_mandir}/man1/rxdebug.1.*
%doc %{_mandir}/man1/scout.1.*
%doc %{_mandir}/man1/sys.1.*
%doc %{_mandir}/man1/tokens.1.*
%doc %{_mandir}/man1/translate_et.1.*
%doc %{_mandir}/man1/udebug.1.*
%doc %{_mandir}/man1/unlog.1.*
%doc %{_mandir}/man1/vos.1.*
%doc %{_mandir}/man1/vos_*.1.*
%doc %{_mandir}/man1/xstat_cm_test.1.*
%doc %{_mandir}/man1/xstat_fs_test.1.*
%doc %{_mandir}/man5/CellServDB.5.*
%doc %{_mandir}/man5/ThisCell.5.*
%doc %{_mandir}/man5/afsmonitor.5.*
%doc %{_mandir}/man5/butc.5.*
%doc %{_mandir}/man5/butc_logs.5.*
%if %{kauth_support}
%doc %{_mandir}/man5/uss.5.*
%doc %{_mandir}/man5/uss_bulk.5.*
%endif
%doc %{_mandir}/man8/backup.8.*
%doc %{_mandir}/man8/backup_*.8.*
%doc %{_mandir}/man8/bos.8.*
%doc %{_mandir}/man8/bos_*.8.*
%doc %{_mandir}/man8/butc.8.*
%doc %{_mandir}/man8/fms.8.*
%doc %{_mandir}/man8/fstrace.8.*
%doc %{_mandir}/man8/fstrace_*.8.*
%doc %{_mandir}/man8/read_tape.8.*
%if %{kauth_support}
%doc %{_mandir}/man8/uss.8.*
%doc %{_mandir}/man8/uss_*.8.*
%endif
# Exclude obsolete or unused files.
%exclude %{_bindir}/livesys
%exclude %{_sbindir}/rmtsysd
%exclude %{_mandir}/man1/dlog.1.*
%exclude %{_mandir}/man1/livesys.1.*
%exclude %{_mandir}/man1/symlink.1.*
%exclude %{_mandir}/man1/symlink_list.1.*
%exclude %{_mandir}/man1/symlink_make.1.*
%exclude %{_mandir}/man1/symlink_remove.1.*
%exclude %{_mandir}/man8/aklog_dynamic_auth.8.*
%exclude %{_mandir}/man8/rmtsysd.8.*
%exclude %{_mandir}/man8/xfs_size_check.8.*
%if ! %{build_authlibs}
%exclude %{_libdir}/libafsauthent.so*
%exclude %{_libdir}/libafsrpc.so*
%exclude %{_libdir}/libkopenafs.so*
%endif
%if ! %{kauth_support}
%exclude %{_bindir}/tokens.krb
%exclude %{_bindir}/pagsh.krb
%exclude %{_mandir}/man5/AuthLog.5.*
%exclude %{_mandir}/man5/AuthLog.dir.5.*
%exclude %{_sbindir}/uss
%exclude %{_mandir}/man5/uss.5.*
%exclude %{_mandir}/man5/uss_bulk.5.*
%exclude %{_mandir}/man8/uss.8.*
%exclude %{_mandir}/man8/uss_*.8.*
%endif
%if ! %{krb5support}
%exclude %{_mandir}/man8/akeyconvert.*
%exclude %{_mandir}/man8/asetkey.*
%endif

%files docs
%doc doc/pdf

%files client
%dir %{_prefix}/vice
%dir %{_prefix}/vice/cache
%dir %{_prefix}/vice/etc
%dir %{_prefix}/vice/etc/C
%{_prefix}/vice/etc/CellServDB.dist
%config(noreplace) %{_prefix}/vice/etc/CellServDB.local
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
%doc %{_mandir}/man1/cmdebug.1.*
%doc %{_mandir}/man1/up.1.*
%doc %{_mandir}/man5/afs.5.*
%doc %{_mandir}/man5/afs_cache.5.*
%doc %{_mandir}/man5/afs_volume_header.5.*
%doc %{_mandir}/man5/afszcm.cat.5.*
%doc %{_mandir}/man5/cacheinfo.5.*
%doc %{_mandir}/man8/afsd.8.*
%doc %{_mandir}/man8/vsys.8.*
%doc %{_mandir}/man5/CellAlias.5.*

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
%doc %{_mandir}/man5/BackupLog.5.*
%doc %{_mandir}/man5/BosConfig.5.*
%doc %{_mandir}/man5/BosLog.5.*
%doc %{_mandir}/man5/FORCESALVAGE.5.*
%doc %{_mandir}/man5/FileLog.5.*
%doc %{_mandir}/man5/KeyFile.5.*
%doc %{_mandir}/man5/KeyFileExt.5.*
%doc %{_mandir}/man5/NetInfo.5.*
%doc %{_mandir}/man5/NetRestrict.5.*
%doc %{_mandir}/man5/NoAuth.5.*
%doc %{_mandir}/man5/PtLog.5.*
%doc %{_mandir}/man5/SALVAGE.fs.5.*
%doc %{_mandir}/man5/SalvageLog.5.*
%doc %{_mandir}/man5/sysid.5.*
%doc %{_mandir}/man5/UserList.5.*
%doc %{_mandir}/man5/VLLog.5.*
%doc %{_mandir}/man5/VolserLog.5.*
%doc %{_mandir}/man5/bdb.DB0.5.*
%doc %{_mandir}/man5/fms.log.5.*
%doc %{_mandir}/man5/krb.conf.5.*
%doc %{_mandir}/man5/krb.excl.5.*
%doc %{_mandir}/man5/prdb.DB0.5.*
%doc %{_mandir}/man5/salvage.lock.5.*
%doc %{_mandir}/man5/tapeconfig.5.*
%doc %{_mandir}/man5/vldb.DB0.5.*
%doc %{_mandir}/man8/bosserver.8.*
%doc %{_mandir}/man8/buserver.8.*
%doc %{_mandir}/man8/fileserver.8.*
%doc %{_mandir}/man8/dafileserver.8.*
%doc %{_mandir}/man8/dafssync-debug.8.*
%doc %{_mandir}/man8/dafssync-debug_*.8.*
%doc %{_mandir}/man8/dasalvager.8.*
%doc %{_mandir}/man8/davolserver.8.*
%doc %{_mandir}/man8/fssync-debug.8.*
%doc %{_mandir}/man8/fssync-debug_*.8.*
%doc %{_mandir}/man8/prdb_check.8.*
%doc %{_mandir}/man8/ptserver.8.*
%doc %{_mandir}/man8/pt_util.8.*
%doc %{_mandir}/man8/salvager.8.*
%doc %{_mandir}/man8/salvageserver.8.*
%doc %{_mandir}/man8/state_analyzer.8.*
%doc %{_mandir}/man8/upclient.8.*
%doc %{_mandir}/man8/upserver.8.*
%doc %{_mandir}/man8/vldb_check.8.*
%doc %{_mandir}/man8/vldb_convert.8.*
%doc %{_mandir}/man8/vlserver.8.*
%doc %{_mandir}/man8/voldump.8.*
%doc %{_mandir}/man8/volinfo.8.*
%doc %{_mandir}/man8/volscan.8.*
%doc %{_mandir}/man8/volserver.8.*

%if %{build_authlibs}
%files authlibs
%{_libdir}/libafsauthent.so.*
%{_libdir}/libafsrpc.so.*
%{_libdir}/libkopenafs.so.*
%endif

%files authlibs-devel
%{_includedir}/kopenafs.h
%{_libdir}/libafsauthent.a
%{_libdir}/libafscp.a
%{_libdir}/libafsrpc.a
%{_libdir}/libafsauthent_pic.a
%{_libdir}/libafsrpc_pic.a
%{_libdir}/libkopenafs.a
%if %{build_authlibs}
%{_libdir}/libafsauthent.so
%{_libdir}/libafsrpc.so
%{_libdir}/libkopenafs.so
%endif

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
%doc %{_mandir}/man1/rxgen.1.*
%doc %{_mandir}/man1/afs_compile_et.1.*
%{_libdir}/perl/AFS/ukernel.pm
%{_libdir}/perl/ukernel.so
%doc %{_mandir}/man3/AFS::ukernel.3.*

%if %{build_dkmspkg}
%files -n dkms-%{name}
%{_prefix}/src/%{name}-%{dkms_version}
%endif

%files kernel-source
%doc %{_prefix}/src/openafs-kernel-%{afsvers}/LICENSE.IBM
%doc %{_prefix}/src/openafs-kernel-%{afsvers}/LICENSE.Sun
%doc %{_prefix}/src/openafs-kernel-%{afsvers}/README
%{_prefix}/src/openafs-kernel-%{afsvers}/src

%files compat
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
%if %{kauth_support}
%ghost %{afswsdir}/etc/uss
%endif
%ghost %{afswsdir}/etc/vos
%ghost %{afswsdir}/etc/vsys

%if %{kauth_support}
%files kauth-client
%{_sbindir}/kas
%{_bindir}/klog
%{_bindir}/klog.krb
%{pamdir}/pam_afs.krb.so.1
%{pamdir}/pam_afs.krb.so
%{pamdir}/pam_afs.so.1
%{pamdir}/pam_afs.so
%{_bindir}/kapasswd
%{_bindir}/kpwvalid
%{_bindir}/pagsh.krb
%{_bindir}/tokens.krb
%ghost %{afswsdir}/bin/kapasswd
%ghost %{afswsdir}/bin/klog
%ghost %{afswsdir}/bin/klog.krb
%ghost %{afswsdir}/bin/pagsh.krb
%ghost %{afswsdir}/bin/tokens.krb
%ghost %{afswsdir}/etc/kas
%doc %{_mandir}/man1/kapasswd.1.*
%doc %{_mandir}/man1/klog.1.*
%doc %{_mandir}/man1/klog.krb.1.*
%doc %{_mandir}/man1/pagsh.krb.1.*
%doc %{_mandir}/man1/tokens.krb.1.*
%doc %{_mandir}/man8/kpwvalid.8.*
%doc %{_mandir}/man8/kas.8.*
%doc %{_mandir}/man8/kas_*.8.*
%exclude %{_bindir}/knfs
%exclude %{_mandir}/man1/knfs.1.*

%files kauth-server
%{_prefix}/afs/bin/kaserver
%{_prefix}/afs/bin/ka-forwarder
%{_sbindir}/kadb_check
%doc %{_mandir}/man5/AuthLog.5.*
%doc %{_mandir}/man5/AuthLog.dir.5.*
%doc %{_mandir}/man5/kaserver.DB0.5.*
%doc %{_mandir}/man5/kaserverauxdb.5.*
%doc %{_mandir}/man8/kadb_check.8.*
%doc %{_mandir}/man8/ka-forwarder.8.*
%doc %{_mandir}/man8/kaserver.8.*
%exclude %{_prefix}/afs/bin/kdb
%exclude %{_mandir}/man8/kdb.8.*
%endif

%if %{krb5support}
%files krb5
%{_bindir}/aklog
%{_bindir}/klog.krb5
%{_sbindir}/akeyconvert
%{_sbindir}/asetkey
%doc %{_mandir}/man1/aklog.1.*
%doc %{_mandir}/man1/klog.krb5.1.*
%doc %{_mandir}/man8/akeyconvert.8.*
%doc %{_mandir}/man8/asetkey.8.*
%endif
%endif

%if %{build_modules}

%files -n kmod-%{name}
%{kmodulesdir}/extra/%{name}/%{name}.ko

%endif

#-----------------------------------------------------------------------------
# Change log
#-----------------------------------------------------------------------------
%changelog
* Fri Jul 31 2026  Michael Meffie <mmeffie@sinenomine.net>
- Drop support and conditionals for RHEL 7 and older releases

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
  a kernel version with 'smp', 'hugemem', etc.
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
