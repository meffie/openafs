#-----------------------------------------------------------------------------
# OpenAFS spec file for RHEL and compatible distributions
#
# This spec file is used to build OpenAFS RPMs for Red Hat Enterprise Linux
# (RHEL), and RHEL-compatible distributions such as Fedora, CentOS Stream,
# AlmaLinux, Rocky Linux, Oracle Linux, and Amazon Linux.
#
# rpmbuild options:
#
#   --define "openafs_version <version>"  The version of the OpenAFS source archive
#
#   --define "srcball_ext <ext>"          The compression suffix of the source archive
#                                         (Source0): gz, bz2, or xz. (default: xz)
#
#   --define "package_version <version>"  The RPM Version tag. (default: openafs_version)
#
#   --define "package_release <release>"  The RPM Release tag. (default: 1)
#
#   --define "source_date_epoch <epoch>"  The build timestamp. (default: current system time)
#
#   --define "kernel_version <version>"   The kernel version (default: current running kernel)
#
#   --define "ksrcdir <path>"             The path to the kernel headers (default:
#                                         /usr/src/kernels/<kernel_version>)
#
#   --define "kmodulesdir <path>"         Kernel modules installation base path (default:
#                                         /usr/lib/modules/<kernel_version>)
#
#   --without userspace                   Do not build userspace packages (default: --with userspace)
#
#   --without modules                     Do not the build kernel module package (default: --with modules)
#
#   --without dkms                        Do not build the DKMS package (default: --with dkms)
#
#   --with supergroups                    Enable supergroup support (default: --without supergroup)
#
#-----------------------------------------------------------------------------

# Handle old macro names
Source99: openafs-compat.macros
%include %{_specdir}/../SOURCES/openafs-compat.macros

#
# Constants
#

%global common_description %{expand:
The OpenAFS distributed filesystem.  OpenAFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.
}

# Disable link time optimization (lto).
%global _lto_cflags %{nil}

# Disable getting the source date epoch from the change log.
%global source_date_epoch_from_changelog 0

# Define the location to the legacy workstation directory.
%global afswsdir /usr/afsws

# Define the location to the legacy installation directory.
%global afsbindir /usr/afs/bin

#
# Version information
#

%if ! %{defined openafs_version}
%global openafs_version %{nil}
%endif

%if ! %{defined package_version}
%global package_version %{openafs_version}
%endif

%if ! %{defined package_release}
%global package_release 1
%endif

%if ! %{defined dkms_version}
%global dkms_version %{package_version}-%{package_release}%{?dist}
%endif

# The compression suffix of the upstream source archive (Source0).  Recent
# releases are published as .tar.gz, .tar.bz2, and .tar.xz; xz gives the
# smallest download.  Older releases may only have .gz/.bz2 available, so
# override with e.g. --define "srcball_ext bz2" when building those.
%if ! %{defined srcball_ext}
%global srcball_ext xz
%endif

%if ! %{defined source_date_epoch}
%global source_date_epoch %(date +%%s)
%endif

#
# Build conditionals
#

%bcond_without dkms
%bcond_without userspace
%bcond_without modules
%bcond_with    supergroups

#
# Kernel module definitions
#
%if %{with modules}

%if ! %{defined kernel_version}
%global kernel_version %(uname -r)
%endif

%if ! %{defined kmodulesdir}
%global kmodulesdir %{_prefix}/lib/modules/%{kernel_version}
%endif

%if ! %{defined ksrcdir}
%global ksrcdir %{_usrsrc}/kernels/%{kernel_version}
%endif

%endif


Summary: OpenAFS distributed filesystem
Name: openafs
Version: %{package_version}
Release: %{package_release}%{?dist}
License: IBM Public License
URL: https://www.openafs.org
BuildRequires: ncurses-devel
BuildRequires: make
BuildRequires: flex
BuildRequires: bison
BuildRequires: systemd-units
BuildRequires: perl-devel
BuildRequires: swig
BuildRequires: perl(ExtUtils::Embed)
BuildRequires: krb5-devel
%if %{with modules}
BuildRequires: kernel-devel
BuildRequires: elfutils-devel
BuildRequires: kernel-rpm-macros
%endif

ExclusiveArch: %{ix86} x86_64 ia64 s390 s390x sparc64 ppc ppc64 ppc64le aarch64

Source0: https://www.openafs.org/dl/openafs/%{openafs_version}/openafs-%{openafs_version}-src.tar.%{srcball_ext}
Source10: https://www.openafs.org/dl/openafs/%{openafs_version}/RELNOTES-%{openafs_version}
Source11: https://www.openafs.org/dl/openafs/%{openafs_version}/ChangeLog
Source20: https://www.central.org/dl/cellservdb/CellServDB.2025-08-16
Source21: openafs-CellServDB.local
Source30: openafs-cacheinfo
Source32: openafs-client.service
Source33: openafs-client-systemd-helper.sh
Source34: openafs-LICENSE.Sun
Source35: openafs-README
Source37: openafs-server.service
Source39: openafs-ThisCell
Source40: openafs-dkms.conf
Source41: openafs-client.sysconfig
Source42: openafs-server.sysconfig
Source43: openafs-migrate-sysconfig.sh
Source44: openafs-migrate-client-paths.sh
Source45: openafs-migrate-server-paths.sh
Source46: openafs-selinux.cil
Source47: openafs-selinux-relabel.sh

%description
%{common_description}
This package provides common files shared across all the various
OpenAFS packages but are not necessarily tied to a client or server.

%if %{with userspace}

%package client
Summary: OpenAFS Filesystem Client
Requires: %{name} = %{version}
Requires: binutils
Requires: filesystem
%if ! 0%{?amzn}
Requires: filesystem-afs
%endif
Requires: systemd-units
Requires(post): systemd-units
Requires(post): systemd-sysv
Requires(preun): systemd-units
Requires(postun): systemd-units
Requires: %{name}-kmod >= %{version}
Provides: %{name}-kmod-common = %{version}

%description client
%{common_description}
This package provides basic client support to mount and manipulate
files in the AFS filesystem.

%package server
Summary: OpenAFS Filesystem Server
Requires: %{name} = %{version}
Requires: systemd-units
Requires(post): systemd-units, systemd-sysv
Requires(preun): systemd-units
Requires(postun): systemd-units

%description server
%{common_description}
This package provides basic server support to host files in an OpenAFS
Cell.

%if %{with dkms}
%package -n dkms-%{name}
Summary:        DKMS-ready kernel source for OpenAFS distributed filesystem
Provides:       %{name}-kernel = %{version}
Provides:       %{name}-kmod = %{version}
Requires(pre):  dkms
Requires(pre):  make
Requires(pre):  flex
Requires(post): dkms
Requires:       %{name}-kmod-common = %{version}

%description -n dkms-%{name}
%{common_description}
This package provides the source code to allow DKMS to build an
OpenAFS kernel module.
%endif

%package authlibs
Summary: OpenAFS authentication shared libraries

%description authlibs
%{common_description}
This package provides a shared version of libafsrpc and libafsauthent.
None of the programs included with OpenAFS currently use these shared
libraries; however, third-party software that wishes to perform AFS
authentication may link against them.

%package authlibs-devel
Requires: %{name}-authlibs = %{version}-%{release}
Requires: %{name}-devel = %{version}-%{release}
Summary: OpenAFS shared library development

%description authlibs-devel
%{common_description}
This package includes the static versions of libafsrpc and
libafsauthent, and symlinks required for building against the dynamic
libraries.

%package devel
Summary: OpenAFS Development Libraries and Headers
Requires: %{name} = %{version}-%{release}

%description devel
%{common_description}
This package provides static development libraries and headers needed
to compile OpenAFS applications.  Note: OpenAFS currently does not provide
shared libraries.

%package docs
Summary: OpenAFS user and administrator documentation
Requires: %{name} = %{version}-%{release}
BuildRequires: perl-core

%description docs
%{common_description}
This package provides historical reference documentation for OpenAFS.

%package kernel-source
Summary: OpenAFS Kernel Module source tree
Provides: %{name}-kernel = %{version}
Provides: %{name}-kmod = %{version}

%description kernel-source
%{common_description}
This package provides the source code to build your own OpenAFS kernel
module.

%package compat
Summary: OpenAFS client compatibility symlinks
Requires: %{name} = %{version}

%description compat
%{common_description}
This package provides compatibility symlinks in %{afswsdir}.  It is
completely optional, and is only necessary to support legacy
applications and scripts that hard-code the location of OpenAFS client
programs.

%package krb5
Summary: OpenAFS programs to use with krb5
Requires: %{name} = %{version}
BuildRequires: krb5-devel

%description krb5
%{common_description}
This package provides compatibility programs so you can use a
Kerberos realm to authenticate to AFS services.

%endif

%if %{with modules}

%package -n kmod-%{name}
Summary:          OpenAFS kernel module
Provides:         %{name}-kmod = %{version}-%{release}
Provides:         %{name}-kernel = %{version}
# kernel-uname-r is the standard RHEL/Fedora capability (from the
# "kernel-rpm-macros" package) for pinning a kmod to one exact kernel
# build; it needs no epoch handling, unlike the plain kernel package's
# own Version.  The openafs kernel module does deep VFS integration and
# is not kABI-stable, so it is always built and required against one
# exact kernel build -- there is no weak-modules support here, by design.
Requires:         kernel-uname-r = %{kernel_version}
Requires:         %{name}-kmod-common >= %{version}
Requires(post):   /usr/sbin/depmod
Requires(postun): /usr/sbin/depmod
Release:          %{package_release}.%(echo %{kernel_version} | sed 's/\.%{_target_cpu}$//' | tr - _)
BuildRequires:    kernel-devel-uname-r = %{kernel_version}
BuildRequires:    elfutils-libelf-devel
BuildRequires:    gcc
BuildRequires:    make

%description -n kmod-%{name}
%{common_description}
This package provides the %{name} kernel modules built for the Linux
kernel %{kernel_version}.

%endif

#-----------------------------------------------------------------------------
# Preparation stage
#-----------------------------------------------------------------------------
%prep

: @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
: @@@
%if %{with modules}
: @@@ kernel version:     %{kernel_version}
%endif
: @@@ build userspace:    %{with userspace}
: @@@ build modules:      %{with modules}
: @@@ arch:               %{_arch}
: @@@ target cpu:         %{_target_cpu}
: @@@
: @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

%setup -q -n openafs-%{openafs_version}

# Add the change log and release notes to source tree.
cp -p %{SOURCE10} .
cp -p %{SOURCE11} .

#-----------------------------------------------------------------------------
# Build stage
#-----------------------------------------------------------------------------
%build

export SOURCE_DATE_EPOCH=%{source_date_epoch}
%set_build_flags

# configure has no --with-afslogsdir option; afslogsdir is only settable
# by pre-setting the shell/environment variable of the same name, which
# the generated configure script honors via ${afslogsdir=...} defaulting.
export afslogsdir="%{_localstatedir}/log/%{name}"

%configure \
    --disable-strip-binaries \
    --enable-debug \
    --with-krb5 \
    --with-swig \
    --disable-kauth \
    --with-linux-kernel-packaging \
%if %{with modules}
    --enable-kernel-module \
    --with-linux-kernel-headers=%{ksrcdir} \
%else
    --disable-kernel-module \
%endif
%if %{with supergroups}
    --enable-supergroups
%endif

%if %{with userspace}
%if %{with modules}
TARGET=all
%else
TARGET=all_nolibafs
%endif
%else
%if %{with modules}
TARGET=libafs
%else
%{error:At least one of --with userspace or --with modules is required.}
%endif
%endif

%make_build only_libafs_tree $TARGET V=0

#-----------------------------------------------------------------------------
# Install stage
#-----------------------------------------------------------------------------
%install

export SOURCE_DATE_EPOCH=%{source_date_epoch}

%if %{with userspace}

# Install userspace files
make %{_smp_mflags} install_nolibafs DESTDIR="%{buildroot}"

# Install client and server systemd files.
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
install -m 644 %{SOURCE41} %{buildroot}%{_sysconfdir}/sysconfig/%{name}-client
install -m 644 %{SOURCE42} %{buildroot}%{_sysconfdir}/sysconfig/%{name}-server
mkdir -p %{buildroot}%{_unitdir}
install -m 644 %{SOURCE32} %{buildroot}%{_unitdir}/openafs-client.service
install -m 644 %{SOURCE37} %{buildroot}%{_unitdir}/openafs-server.service
install -m 755 %{SOURCE33} %{buildroot}%{_libexecdir}/%{name}/openafs-client-systemd-helper.sh

# Install data migration scripts.
install -m 755 %{SOURCE43} %{buildroot}%{_libexecdir}/%{name}/openafs-migrate-sysconfig.sh
install -m 755 %{SOURCE44} %{buildroot}%{_libexecdir}/%{name}/openafs-migrate-client-paths.sh
install -m 755 %{SOURCE45} %{buildroot}%{_libexecdir}/%{name}/openafs-migrate-server-paths.sh

# Install SELinux policy supplement and setup script for the server.
install -m 755 %{SOURCE47} %{buildroot}%{_libexecdir}/%{name}/openafs-selinux-relabel.sh
mkdir -p %{buildroot}%{_datadir}/%{name}/selinux
install -m 644 %{SOURCE46} %{buildroot}%{_datadir}/%{name}/selinux/openafs-selinux.cil

# Install server directories.
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/server
mkdir -p %{buildroot}%{_localstatedir}/log/%{name}
mkdir -p %{buildroot}%{_localstatedir}/%{name}/db
chmod 700 %{buildroot}%{_localstatedir}/%{name}
chmod 700 %{buildroot}%{_localstatedir}/%{name}/db

# Install client directories and config files.
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
install -p -m 644 %{SOURCE39} %{buildroot}%{_sysconfdir}/%{name}/ThisCell
install -p -m 644 %{SOURCE20} %{buildroot}%{_sysconfdir}/%{name}/CellServDB.dist
install -p -m 644 %{SOURCE21} %{buildroot}%{_sysconfdir}/%{name}/CellServDB.local
install -p -m 644 %{SOURCE30} %{buildroot}%{_sysconfdir}/%{name}/cacheinfo
mkdir -p %{buildroot}%{_localstatedir}/cache/%{name}
chmod 700 %{buildroot}%{_localstatedir}/cache/%{name}

# Install DKMS source.
install -d -m 755 %{buildroot}%{_prefix}/src
cp -a libafs_tree %{buildroot}%{_prefix}/src/%{name}-%{dkms_version}
sed -e 's/@NAME@/%{name}/' \
    -e 's/@PACKAGE_VERSION@/%{dkms_version}/' \
    %{SOURCE40} > %{buildroot}%{_prefix}/src/%{name}-%{dkms_version}/dkms.conf

# Install the kernel module source tree.
mkdir -p %{buildroot}%{_prefix}/src/%{name}-kernel-%{openafs_version}/src
tar cf - -C libafs_tree . | \
    tar xf - -C %{buildroot}%{_prefix}/src/%{name}-kernel-%{openafs_version}/src
install -m 644 LICENSE %{buildroot}%{_prefix}/src/%{name}-kernel-%{openafs_version}/LICENSE.IBM
install -m 644 %{SOURCE34} %{buildroot}%{_prefix}/src/%{name}-kernel-%{openafs_version}/LICENSE.Sun
install -m 644 %{SOURCE35} %{buildroot}%{_prefix}/src/%{name}-kernel-%{openafs_version}/README

%endif

# Install kernel modules
%if %{with modules}

mkdir -p %{buildroot}%{kmodulesdir}/extra/%{name}
install -m 755 \
    src/libafs/MODLOAD-%{kernel_version}/openafs.ko \
    %{buildroot}%{kmodulesdir}/extra/%{name}/%{name}.ko

%endif

#-----------------------------------------------------------------------------
# Check stage
#-----------------------------------------------------------------------------
%check
%if %{with userspace}
make check
%endif

#-----------------------------------------------------------------------------
# Scriptlets
#-----------------------------------------------------------------------------
%if %{with userspace}

# openafs scriptlets
%post
if [ $1 -ge 2 ]; then
    # Migrate the sysconfig file on upgrade.
    /bin/sh %{_libexecdir}/%{name}/openafs-migrate-sysconfig.sh || :
fi

%preun
if [ $1 = 0 ] ; then
    if [ -d /afs ]; then
        rmdir /afs || :
    fi
fi

# openafs-client scriptlets
%post client
if [ $1 -ge 2 ]; then
    # Migrate from the Transarc installation paths on upgrade.
    /bin/sh %{_libexecdir}/%{name}/openafs-migrate-client-paths.sh || :
fi
if [ ! -d /afs ]; then
    # The /afs directory is owned by the filesystem package. As a fallback,
    # ensure the /afs directory exists when the openafs-client package is
    # installed.
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
%pre server
if [ $1 -ge 2 ]; then
    # Ensure servers are stopped on upgrade to do Transarc to FHS
    # path migration.
    /usr/bin/systemctl stop openafs-server.service || :
fi

%post server
if [ $1 -ge 2 ]; then
    # Migrate from the Transarc installation paths on upgrade.
    /bin/sh %{_libexecdir}/%{name}/openafs-migrate-server-paths.sh || :
fi
# Create compat symlinks
mkdir -p %{afsbindir}
ln -sf %{_sbindir}/bosserver %{afsbindir}/bosserver
ln -sf %{_libexecdir}/%{name}/buserver %{afsbindir}/buserver
ln -sf %{_libexecdir}/%{name}/dafileserver %{afsbindir}/dafileserver
ln -sf %{_libexecdir}/%{name}/dasalvager %{afsbindir}/dasalvager
ln -sf %{_libexecdir}/%{name}/davolserver %{afsbindir}/davolserver
ln -sf %{_libexecdir}/%{name}/fileserver %{afsbindir}/fileserver
ln -sf %{_libexecdir}/%{name}/ptserver %{afsbindir}/ptserver
ln -sf %{_libexecdir}/%{name}/salvager %{afsbindir}/salvager
ln -sf %{_libexecdir}/%{name}/salvageserver %{afsbindir}/salvageserver
ln -sf %{_libexecdir}/%{name}/upclient %{afsbindir}/upclient
ln -sf %{_libexecdir}/%{name}/upserver %{afsbindir}/upserver
ln -sf %{_libexecdir}/%{name}/vlserver %{afsbindir}/vlserver
ln -sf %{_libexecdir}/%{name}/volserver %{afsbindir}/volserver
[ -x /sbin/restorecon ] && /sbin/restorecon -R %{afsbindir}
# Register SELinux file contexts and policy for the FHS server paths.
/bin/sh %{_libexecdir}/%{name}/openafs-selinux-relabel.sh install \
    %{_datadir}/%{name}/selinux/openafs-selinux.cil || :
# Run the systemd post scriptlet for the server.
%systemd_post openafs-server.service

%preun server
if [ $1 = 0 ]; then
    # Final removal: drop the SELinux customizations added on install,
    # while the script installed by this package still exists on disk.
    /bin/sh %{_libexecdir}/%{name}/openafs-selinux-relabel.sh remove \
        %{_datadir}/%{name}/selinux/openafs-selinux.cil || :
fi
%systemd_preun openafs-server.service

%postun server
%systemd_postun_with_restart openafs-server.service

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
ln -sf %{_sbindir}/vos          %{afswsdir}/etc/vos
ln -sf %{_sbindir}/vsys         %{afswsdir}/etc/vsys

%postun compat
if [ $1 = 0 ] ; then
    rmdir %{afswsdir}/bin >/dev/null 2>/dev/null || :
    rmdir %{afswsdir}/etc >/dev/null 2>/dev/null || :
    rmdir %{afswsdir} >/dev/null 2>/dev/null || :
fi

# dkms-openafs scriptlets
%if %{with dkms}
%post -n dkms-%{name}
dkms add -m %{name} -v %{dkms_version} --rpm_safe_upgrade
dkms build -m %{name} -v %{dkms_version} --rpm_safe_upgrade
dkms install -m %{name} -v %{dkms_version} --rpm_safe_upgrade

%preun -n dkms-%{name}
dkms remove -m %{name} -v %{dkms_version} --rpm_safe_upgrade --all ||:
%endif
%endif

# kmod-openafs scriptlets
%if %{with modules}
%post -n kmod-%{name}
/usr/sbin/depmod -aeF /boot/System.map-%{kernel_version} %{kernel_version} > /dev/null || :

%postun -n kmod-%{name}
/usr/sbin/depmod -aF /boot/System.map-%{kernel_version} %{kernel_version} &> /dev/null || :
%endif

#-----------------------------------------------------------------------------
# File lists
#-----------------------------------------------------------------------------
%if %{with userspace}

%files
%dir %{_libexecdir}/%{name}
%doc LICENSE
%doc ChangeLog
%doc RELNOTES-%{openafs_version}
%{_libexecdir}/%{name}/openafs-migrate-sysconfig.sh
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
%doc %{_mandir}/man8/backup.8.*
%doc %{_mandir}/man8/backup_*.8.*
%doc %{_mandir}/man8/bos.8.*
%doc %{_mandir}/man8/bos_*.8.*
%doc %{_mandir}/man8/butc.8.*
%doc %{_mandir}/man8/fms.8.*
%doc %{_mandir}/man8/fstrace.8.*
%doc %{_mandir}/man8/fstrace_*.8.*
%doc %{_mandir}/man8/read_tape.8.*
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
%exclude %{_bindir}/tokens.krb
%exclude %{_bindir}/pagsh.krb
%exclude %{_mandir}/man5/AuthLog.5.*
%exclude %{_mandir}/man5/AuthLog.dir.5.*
%exclude %{_sbindir}/uss
%exclude %{_mandir}/man5/uss.5.*
%exclude %{_mandir}/man5/uss_bulk.5.*
%exclude %{_mandir}/man8/uss.8.*
%exclude %{_mandir}/man8/uss_*.8.*

%files docs
%doc doc/pdf

%files client
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/C
%dir %{_libexecdir}/%{name}
%dir %{_localstatedir}/cache/openafs
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/cacheinfo
%config(noreplace) %{_sysconfdir}/%{name}/CellServDB.dist
%config(noreplace) %{_sysconfdir}/%{name}/CellServDB.local
%config(noreplace) %{_sysconfdir}/%{name}/ThisCell
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}-client
%{_bindir}/afsio
%{_bindir}/cmdebug
%{_bindir}/up
%{_sbindir}/afsd
%{_datadir}/%{name}/C/afszcm.cat
%{_libdir}/libuafs.a
%{_libdir}/libuafs_pic.a
%{_unitdir}/openafs-client.service
%{_libexecdir}/%{name}/openafs-client-systemd-helper.sh
%{_libexecdir}/%{name}/openafs-migrate-client-paths.sh
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
%dir %{_libexecdir}/%{name}
%dir %{_localstatedir}/%{name}
%dir %{_localstatedir}/%{name}/db
%dir %{_localstatedir}/log/%{name}
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/server
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/selinux
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}-server
%{_sbindir}/bosserver
%{_sbindir}/bos_util
%{_libexecdir}/%{name}/buserver
%{_libexecdir}/%{name}/dafileserver
%{_libexecdir}/%{name}/dasalvager
%{_libexecdir}/%{name}/davolserver
%{_libexecdir}/%{name}/fileserver
%{_libexecdir}/%{name}/openafs-migrate-server-paths.sh
%{_libexecdir}/%{name}/openafs-selinux-relabel.sh
%{_datadir}/%{name}/selinux/openafs-selinux.cil
%{_libexecdir}/%{name}/ptserver
%{_libexecdir}/%{name}/salvager
%{_libexecdir}/%{name}/salvageserver
%{_libexecdir}/%{name}/upclient
%{_libexecdir}/%{name}/upserver
%{_libexecdir}/%{name}/vlserver
%{_libexecdir}/%{name}/volserver
%{_sbindir}/dafssync-debug
%{_sbindir}/fssync-debug
%{_sbindir}/pt_util
%{_sbindir}/salvsync-debug
%{_sbindir}/state_analyzer
%{_sbindir}/volinfo
%{_sbindir}/volscan
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
# Compat symlinks
%ghost %{afsbindir}/bosserver
%ghost %{afsbindir}/buserver
%ghost %{afsbindir}/dafileserver
%ghost %{afsbindir}/dasalvager
%ghost %{afsbindir}/davolserver
%ghost %{afsbindir}/fileserver
%ghost %{afsbindir}/ptserver
%ghost %{afsbindir}/salvager
%ghost %{afsbindir}/salvageserver
%ghost %{afsbindir}/upclient
%ghost %{afsbindir}/upserver
%ghost %{afsbindir}/vlserver
%ghost %{afsbindir}/volserver

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
%doc %{_mandir}/man1/rxgen.1.*
%doc %{_mandir}/man1/afs_compile_et.1.*
%{_libdir}/perl/AFS/ukernel.pm
%{_libdir}/perl/ukernel.so
%doc %{_mandir}/man3/AFS::ukernel.3.*

%if %{with dkms}
%files -n dkms-%{name}
%{_prefix}/src/%{name}-%{dkms_version}
%endif

%files kernel-source
%doc %{_prefix}/src/%{name}-kernel-%{openafs_version}/LICENSE.IBM
%doc %{_prefix}/src/%{name}-kernel-%{openafs_version}/LICENSE.Sun
%doc %{_prefix}/src/%{name}-kernel-%{openafs_version}/README
%{_prefix}/src/%{name}-kernel-%{openafs_version}/src

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
%ghost %{afswsdir}/etc/vos
%ghost %{afswsdir}/etc/vsys

%files krb5
%{_bindir}/aklog
%{_bindir}/klog.krb5
%{_bindir}/akeyconvert
%{_bindir}/asetkey
%doc %{_mandir}/man1/aklog.1.*
%doc %{_mandir}/man1/klog.krb5.1.*
%doc %{_mandir}/man8/akeyconvert.8.*
%doc %{_mandir}/man8/asetkey.8.*
%endif

%if %{with modules}

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
