# OpenAFS Platform Support

## Introduction

This document establishes the platform support policy for the OpenAFS project
to provide a clear understanding of which platforms are actively maintained.
This policy helps focus development resources and provides transparency to the
user community.

The OpenAFS project categorizes platform support into the following three tiers:

**Tier 1: Maintained**

Tier 1 platforms are currently supported platforms.  The OpenAFS project focuses
its development and testing resources on these platforms.  The OpenAFS project
is committed to addressing bugs reported on Tier 1 platforms in a timely
manner, including providing fixes in subsequent maintenance releases.

**Tier 2: Best-Effort**

Tier 2 platforms are those for which we provide limited support. While they are
expected to work, they may not be a part of our regular testing for every code
change.

The OpenAFS project does not actively develop or test on these platforms, and
support often relies on community members with access to the hardware.

Issues on Tier 2 platforms will not prevent a new release.

**Tier 3: Legacy**

Tier 3 platforms are no longer actively supported by the OpenAFS project.
While the code for these platforms is currently retained in the source tree, it
may be removed in a future release if it impedes new development.

The OpenAFS project will not investigate issues or accept patches for these
platforms. OpenAFS is not guaranteed to compile or run on these systems, and
platform-specific code may be removed in new releases.


## Tier 1: Maintained

The following architectures are classified as Tier 1:

- `x86_64`
- `aarch64`

The following platforms are classified as Tier 1:

- Red Hat Enterprise Linux 8, 9, 10, and derivatives
- CentOS-Stream 9, 10
- Fedora (current version)
- Oracle Linux 8, 9, 10
- openSUSE Leap 15.6, 16.0
- openSUSE Tumbleweed
- Debian 12 (Bookworm)
- Debian 13 (Trixie)
- Ubuntu LTS 22.04, 24.04, 26.04
- Apple macOS 26 (Tahoe)
- Apple macOS 15 (Sequoia)
- Apple macOS 14 (Sonoma)
- Oracle Solaris 11.4 `x86_64`
- IBM AIX 7.1, 7.2, 7.3


## Tier 2: Best-Effort

The following architectures are classified as Tier 2:

- `ppc64le`
- `s390` (32-bit)
- `i386`
- `arm`

The following platforms classified as Tier 2:

### Linux distributions

- Red Hat Enterprise Linux 6, and derivatives
- Debian ?
- Ubuntu LTS ?
- IBM AIX 6 ?

### Unix-family systems

- All other Linux distributions (minimum Linux kernel is 2.6.18)
- FreeBSD 14
- FreeBSD 13  (EOL: 2026-04-30)
- Oracle Solaris 11.3 (EOL: 2027-01-31)
- Oracle Solaris 10 (EOL: 2027-01-31)
- NetBSD 9 and later
- OpenBSD 6.5 and later

### Microsoft Windows

The OpenAFS client is supported as a Tier 2 platform on the following 64-bit
Microsoft Windows products.  (The OpenAFS server platforms are classified as
Tier 3: Legacy on all Microsoft Windows versions.)

- Microsoft Windows 11
- Microsoft Windows 10
- Microsoft Windows Server 2025
- Microsoft Windows Server 2022
- Microsoft Windows Server 2019
- Microsoft Windows Server 2016


## Tier 3: Legacy

The following architectures are classified as Tier 3:

- Alpha
- Itanium
- PA-RISC
- PowerPC
- SPARC

The following platforms are classified as Tier 3:

#### Legacy Apple macOS versions

- Apple macOS 13 (Ventura) (EOL: 2025-09-15)
- Apple macOS 12 (Monterey) (EOL: 2024-09-16)
- Apple macOS 11 (Big Sur)  (EOL: 2023-09-26)
- Apple macOS 10.15 (Catalina) (EOL: 2022-09-12)
- Apple macOS 10.14 (Mojave)  (EOL: 2021-10-25)
- Apple macOS 10.13 (High Sierra) (EOL: 2020-12-01)
- Apple macOS 10.12 (Sierra) (EOL: 2019-10-01)
- Apple OS X 10.11 (El Capitan) (EOL: 2018-09-01)
- Apple OS X 10.10 (Yosemite) (EOL: 2017-08-01)
- Apple OS X 10.9 (Mavericks) (EOL: 2016-12-01)
- Apple OS X 10.8 (Mountain Lion) (EOL: 2015-08-01)
- Apple Mac OS X 10.7 (Lion) (EOL: 2014-10-01)
- Apple Mac OS X 10.6 (Snow Leopard) (EOL: 2014-02-01)
- Apple Mac OS X 10.5 (Leopard) (EOL: 2011-06-01)
- Apple Mac OS X 10.4 (Tiger) (EOL: 2009-09-01)
- Apple Mac OS X 10.3 (Panther) (EOL: 2005-04-01)

#### Legacy Microsoft Windows versions

OpenAFS server components on the Windows platform are classified as legacy on
all Microsoft Windows products.  The OpenAFS client is no longer supported on
the following Microsoft Windows products.

- Microsoft Windows 2000 (EOL: 2010-07-13)
- Microsoft Windows XP (EOL: 2014-04-08)
- Microsoft Windows Server 2003 (EOL: 2015-07-14)
- Microsoft Windows 8 (EOL: 2016-01-12)
- Microsoft Windows Vista (EOL: 2017-04-11)
- Microsoft Windows 7 (EOL: 2020-01-14)
- Microsoft Windows Server 2008 (EOL: 2020-01-14)
- Microsoft Windows 8.1 (EOL: 2023-01-10)
- Microsoft Windows Server 2012 (EOL: 2023-10-10)

#### Legacy Unix-family systems

- IBM AIX 6.1 (EOL: 2017-04-30)
- IBM AIX 5.3 (EOL: 2012-04-30)
- IBM AIX 5.2 (EOL: 2009-04-30)
- IBM AIX 5.1 (EOL: 2006-04-01)
- IBM AIX 4.x (EOL: 2003-12-31)
- Oracle Solaris 9 and older (EOL: 2014-10-31)
- FreeBSD 12 and older (EOL: 2022-06-30)
- NetBSD 8 and older  (EOL: 2022-02-14)
- OpenBSD 6.4 and older (EOL: 2019-10-17)
- SGI IRIX
- HP-UX
- DragonFly BSD

## OpenAFS System Names

The following table maps the OpenAFS `sysname` identifiers to their
corresponding platform and support tier.

|   OpenAFS sysname    | Tier | Description                                           |
|----------------------|------|-------------------------------------------------------|
|  `alpha_linux_26`    |   3  | Linux 2.6.x (Digital Alpha)                           |
|  `alpha_nbsd15`      |   3  | NetBSD 1.5 (Digital Alpha)                            |
|  `alpha_nbsd16`      |   3  | NetBSD 1.6 (Digital Alpha)                            |
|  `amd64_darwin_100`  |   3  | Apple Mac OS X 10.6 "Snow Leopard" (Intel 64)         |
|  `amd64_darwin_110`  |   3  | Apple Mac OS X 10.7 "Lion" (Intel 64)                 |
|  `amd64_darwin_120`  |   3  | Apple OS X 10.8 "Mountain Lion" (Intel 64)            |
|  `amd64_darwin_130`  |   3  | Apple OS X 10.9 "Mavericks" (Intel 64)                |
|  `amd64_darwin_140`  |   3  | Apple OS X 10.10 "Yosemite" (Intel 64)                |
|  `amd64_darwin_150`  |   3  | Apple OS X 10.11 "El Capitan" (Intel 64)              |
|  `amd64_darwin_160`  |   3  | Apple macOS 10.12 "Sierra" (Intel 64)                 |
|  `amd64_darwin_170`  |   3  | Apple macOS 10.13 "High Sierra" (Intel 64)            |
|  `amd64_darwin_180`  |   3  | Apple macOS 10.14 "Mojave" (Intel 64)                 |
|  `amd64_darwin_190`  |   3  | Apple macOS 10.15 "Catalina" (Intel 64)               |
|  `amd64_darwin_200`  |   3  | Apple macOS 11 "Big Sur" (Intel 64)                   |
|  `amd64_darwin_210`  |   3  | Apple macOS 12 "Monterey" (Intel 64)                  |
|  `amd64_darwin_220`  |   3  | Apple macOS 13 "Ventura" (Intel 64)                   |
|  `amd64_darwin_230`  |   1  | Apple macOS 14 "Sonoma" (Intel 64)                    |
|  `amd64_darwin_240`  |   1  | Apple macOS 15 "Sequoia" (Intel 64)                   |
|  `amd64_darwin_250`  |   1  | Apple macOS 26 "Tahoe" (Intel 64)                     |
|  `amd64_fbsd_100`    |   3  | FreeBSD 10.0 (amd64)                                  |
|  `amd64_fbsd_101`    |   3  | FreeBSD 10.1 (amd64)                                  |
|  `amd64_fbsd_102`    |   3  | FreeBSD 10.2 (amd64)                                  |
|  `amd64_fbsd_103`    |   3  | FreeBSD 10.3 (amd64)                                  |
|  `amd64_fbsd_104`    |   3  | FreeBSD 10.4 (amd64)                                  |
|  `amd64_fbsd_110`    |   3  | FreeBSD 11.0 (amd64)                                  |
|  `amd64_fbsd_111`    |   3  | FreeBSD 11.1 (amd64)                                  |
|  `amd64_fbsd_112`    |   3  | FreeBSD 11.2 (amd64)                                  |
|  `amd64_fbsd_113`    |   3  | FreeBSD 11.3 (amd64)                                  |
|  `amd64_fbsd_120`    |   3  | FreeBSD 12.0 (amd64)                                  |
|  `amd64_fbsd_121`    |   3  | FreeBSD 12.1 (amd64)                                  |
|  `amd64_fbsd_122`    |   3  | FreeBSD 12.2 (amd64)                                  |
|  `amd64_fbsd_123`    |   3  | FreeBSD 12.3 (amd64)                                  |
|  `amd64_fbsd_130`    |   2  | FreeBSD 13.0 (amd64)                                  |
|  `amd64_fbsd_131`    |   2  | FreeBSD 13.1 (amd64)                                  |
|  `amd64_fbsd_140`    |   2  | FreeBSD 14.0 (amd64)                                  |
|  `amd64_fbsd_141`    |   2  | FreeBSD 14.1 (amd64)                                  |
|  `amd64_linux26`     |   1  | Linux 2.6+ (amd64)                                    |
|  `amd64_nbsd20`      |   3  | NetBSD 2.0 (amd64)                                    |
|  `amd64_nbsd30`      |   3  | NetBSD 3.0 (amd64)                                    |
|  `amd64_nbsd40`      |   3  | NetBSD 4.0 (amd64)                                    |
|  `amd64_nbsd50`      |   3  | NetBSD 5.0 (amd64)                                    |
|  `amd64_nbsd60`      |   3  | NetBSD 6.0 (amd64)                                    |
|  `amd64_nbsd70`      |   3  | NetBSD 7.0 (amd64)                                    |
|  `amd64_obsd36`      |   3  | OpenBSD 3.6 (amd64)                                   |
|  `amd64_obsd37`      |   3  | OpenBSD 3.7 (amd64)                                   |
|  `amd64_obsd38`      |   3  | OpenBSD 3.8 (amd64)                                   |
|  `amd64_obsd39`      |   3  | OpenBSD 3.9 (amd64)                                   |
|  `amd64_obsd40`      |   3  | OpenBSD 4.0 (amd64)                                   |
|  `amd64_obsd41`      |   3  | OpenBSD 4.1 (amd64)                                   |
|  `amd64_obsd42`      |   3  | OpenBSD 4.2 (amd64)                                   |
|  `amd64_obsd43`      |   3  | OpenBSD 4.3 (amd64)                                   |
|  `amd64_obsd44`      |   3  | OpenBSD 4.4 (amd64)                                   |
|  `amd64_obsd45`      |   3  | OpenBSD 4.5 (amd64)                                   |
|  `amd64_obsd46`      |   3  | OpenBSD 4.6 (amd64)                                   |
|  `amd64_obsd47`      |   3  | OpenBSD 4.7 (amd64)                                   |
|  `amd64_obsd48`      |   3  | OpenBSD 4.8 (amd64)                                   |
|  `amd64_obsd49`      |   3  | OpenBSD 4.9 (amd64)                                   |
|  `amd64_obsd50`      |   3  | OpenBSD 5.0 (amd64)                                   |
|  `amd64_obsd51`      |   3  | OpenBSD 5.1 (amd64)                                   |
|  `amd64_obsd52`      |   3  | OpenBSD 5.2 (amd64)                                   |
|  `amd64_obsd53`      |   3  | OpenBSD 5.3 (amd64)                                   |
|  `amd64_obsd54`      |   3  | OpenBSD 5.4 (amd64)                                   |
|  `arm64_linux26`     |   1  | Linux 2.6+ (arm64)                                    |
|  `arm_darwin_100`    |   3  | Apple Mac OS X 10.6 "Snow Leopard" (Apple iPhone)     |
|  `arm_darwin_200`    |   3  | Apple macOS 11 "Big Sur" (Apple Silicon)              |
|  `arm_darwin_210`    |   3  | Apple macOS 12 "Monterey" (Apple Silicon)             |
|  `arm_darwin_220`    |   3  | Apple macOS 13 "Ventura" (Apple Silicon)              |
|  `arm_darwin_230`    |   1  | Apple macOS 14 "Sonoma" (Apple Silicon)               |
|  `arm_darwin_240`    |   1  | Apple macOS 15 "Sequoia" (Apple Silicon)              |
|  `arm_darwin_250`    |   1  | Apple macOS 26 "Tahoe" (Apple Silicon)                |
|  `arm_linux26`       |   2  | Linux 2.6+ (32-bit ARM)                               |
|  `hp_ux102`          |   3  | HP/UX 10.20 (32-bit PA-RISC)                          |
|  `hp_ux110`          |   3  | HP/UX 11.00 (64-bit PA-RISC)                          |
|  `hp_ux1123`         |   3  | HP/UX 11.23/11i v2 (64-bit PA-RISC)                   |
|  `hp_ux11i`          |   3  | HP/UX 11.11/11i v1 (64-bit PA-RISC)                   |
|  `i386_dfbsd_23`     |   3  | DragonFly BSD 2.3 (i386)                              |
|  `i386_fbsd_100`     |   3  | FreeBSD 10.0 (i386)                                   |
|  `i386_fbsd_101`     |   3  | FreeBSD 10.1 (i386)                                   |
|  `i386_fbsd_102`     |   3  | FreeBSD 10.2 (i386)                                   |
|  `i386_fbsd_103`     |   3  | FreeBSD 10.3 (i386)                                   |
|  `i386_fbsd_104`     |   3  | FreeBSD 10.4 (i386)                                   |
|  `i386_fbsd_110`     |   3  | FreeBSD 11.0 (i386)                                   |
|  `i386_fbsd_111`     |   3  | FreeBSD 11.1 (i386)                                   |
|  `i386_fbsd_112`     |   3  | FreeBSD 11.2 (i386)                                   |
|  `i386_fbsd_113`     |   3  | FreeBSD 11.3 (i386)                                   |
|  `i386_fbsd_120`     |   3  | FreeBSD 12.0 (i386)                                   |
|  `i386_fbsd_121`     |   3  | FreeBSD 12.1 (i386)                                   |
|  `i386_fbsd_122`     |   3  | FreeBSD 12.2 (i386)                                   |
|  `i386_fbsd_123`     |   3  | FreeBSD 12.3 (i386)                                   |
|  `i386_linux26`      |   2  | Linux 2.6+ (i386)                                     |
|  `i386_nbsd15`       |   3  | NetBSD 1.5 (i386)                                     |
|  `i386_nbsd16`       |   3  | NetBSD 1.6 (i386)                                     |
|  `i386_nbsd20`       |   3  | NetBSD 2.0 (i386)                                     |
|  `i386_nbsd21`       |   3  | NetBSD 2.1 (i386)                                     |
|  `i386_nbsd30`       |   3  | NetBSD 3.0 (i386)                                     |
|  `i386_nbsd40`       |   3  | NetBSD 4.0 (i386)                                     |
|  `i386_nbsd50`       |   3  | NetBSD 5.0 (i386)                                     |
|  `i386_nbsd60`       |   3  | NetBSD 6.0 (i386)                                     |
|  `i386_nbsd70`       |   3  | NetBSD 7.0 (i386)                                     |
|  `i386_obsd31`       |   3  | OpenBSD 3.1 (i386)                                    |
|  `i386_obsd32`       |   3  | OpenBSD 3.2 (i386)                                    |
|  `i386_obsd33`       |   3  | OpenBSD 3.3 (i386)                                    |
|  `i386_obsd34`       |   3  | OpenBSD 3.4 (i386)                                    |
|  `i386_obsd35`       |   3  | OpenBSD 3.5 (i386)                                    |
|  `i386_obsd36`       |   3  | OpenBSD 3.6 (i386)                                    |
|  `i386_obsd37`       |   3  | OpenBSD 3.7 (i386)                                    |
|  `i386_obsd38`       |   3  | OpenBSD 3.8 (i386)                                    |
|  `i386_obsd39`       |   3  | OpenBSD 3.9 (i386)                                    |
|  `i386_obsd40`       |   3  | OpenBSD 4.0 (i386)                                    |
|  `i386_obsd41`       |   3  | OpenBSD 4.1 (i386)                                    |
|  `i386_obsd42`       |   3  | OpenBSD 4.2 (i386)                                    |
|  `i386_obsd43`       |   3  | OpenBSD 4.3 (i386)                                    |
|  `i386_obsd44`       |   3  | OpenBSD 4.4 (i386)                                    |
|  `i386_obsd45`       |   3  | OpenBSD 4.5 (i386)                                    |
|  `i386_obsd46`       |   3  | OpenBSD 4.6 (i386)                                    |
|  `i386_obsd47`       |   3  | OpenBSD 4.7 (i386)                                    |
|  `i386_obsd48`       |   3  | OpenBSD 4.8 (i386)                                    |
|  `i386_obsd49`       |   3  | OpenBSD 4.9 (i386)                                    |
|  `i386_obsd50`       |   3  | OpenBSD 5.0 (i386)                                    |
|  `i386_obsd51`       |   3  | OpenBSD 5.1 (i386)                                    |
|  `i386_obsd52`       |   3  | OpenBSD 5.2 (i386)                                    |
|  `i386_obsd53`       |   3  | OpenBSD 5.3 (i386)                                    |
|  `i386_obsd54`       |   3  | OpenBSD 5.4 (i386)                                    |
|  `i386_umlinux26`    |   3  | User-mode Linux 2.6 (i386)                            |
|  `ia64_hpux1122`     |   3  | HP-UX 11.22 (Itanium)                                 |
|  `ia64_hpux1123`     |   3  | HP-UX 11.23 (Itanium)                                 |
|  `ia64_linux26`      |   3  | Linux 2.6+ (Itanium)                                  |
|  `macppc_nbsd16`     |   3  | NetBSD 1.6 (Mac PowerPC)                              |
|  `macppc_nbsd20`     |   3  | NetBSD 2.0 (Mac PowerPC)                              |
|  `ppc64_darwin_100`  |   3  | Apple macOS 10.6 "Snow Leopard" (PowerPC 64)          |
|  `ppc64le_linux26`   |   2  | Linux 2.6+ (ppc64le)                                  |
|  `ppc64_linux26`     |   3  | Linux 2.6+ (ppc64)                                    |
|  `ppc_darwin_100`    |   3  | Apple Mac OS X 10.6 "Snow Leopard" (PowerPC 32)       |
|  `ppc_darwin_70`     |   3  | Apple Mac OS X 10.3 "Panther" (PowerPC 32)            |
|  `ppc_darwin_80`     |   3  | Apple Mac OS X 10.4 "Tiger" (PowerPC 32)              |
|  `ppc_darwin_90`     |   3  | Apple Mac OS X 10.5 "Leopard" (PowerPC 32)            |
|  `ppc_linux26`       |   3  | Linux 2.6+ (ppc)                                      |
|  `rs_aix42`          |   3  | IBM AIX 4.2                                           |
|  `rs_aix51`          |   3  | IBM AIX 5.1                                           |
|  `rs_aix52`          |   3  | IBM AIX 5.2                                           |
|  `rs_aix53`          |   ?  | IBM AIX 5.3                                           |
|  `rs_aix61`          |   ?  | IBM AIX 6.1                                           |
|  `rs_aix71`          |   1  | IBM AIX 7.1                                           |
|  `rs_aix72`          |   1  | IBM AIX 7.2                                           |
|  `rs_aix73`          |   1  | IBM AIX 7.3                                           |
|  `s390_linux26`      |   2  | Linux 2.6+ (s390)                                     |
|  `s390x_linux26`     |   2  | Linux 2.6+ (s390x)                                    |
|  `sgi_65`            |   3  | SGI IRIX 6.5                                          |
|  `sparc64_linux26`   |   3  | Linux 2.6+ (SPARC64)                                  |
|  `sparc_linux26`     |   3  | Linux 2.6+ (SPARC)                                    |
|  `sun4x_510`         |   3  | Solaris 10 (SPARC)                                    |
|  `sun4x_511`         |   3  | Solaris 11 (SPARC)                                    |
|  `sun4x_58`          |   3  | Solaris 8 (SPARC)                                     |
|  `sun4x_59`          |   3  | Solaris 9 (SPARC)                                     |
|  `sunx86_510`        |   3  | Solaris 10 (x86)                                      |
|  `sunx86_511`        |   3  | Solaris 11 (x86)                                      |
|  `sunx86_58`         |   3  | Solaris 8 (x86)                                       |
|  `sunx86_59`         |   3  | Solaris 9 (x86)                                       |
|  `x86_darwin_100`    |   3  | Apple Mac OS X 10.6 "Snow Leopard" (Intel 32)         |
|  `x86_darwin_110`    |   3  | Apple Mac OS X 10.7 "Lion" (Intel 32)                 |
|  `x86_darwin_120`    |   3  | Apple OS X 10.8 "Mountain Lion" (Intel 32)            |
|  `x86_darwin_130`    |   3  | Apple OS X 10.9 "Mavericks" (Intel 32)                |
|  `x86_darwin_140`    |   3  | Apple OS X 10.10 "Yosemite" (Intel 32)                |
|  `x86_darwin_150`    |   3  | Apple OS X 10.11 "El Capitan" (Intel 32)              |
|  `x86_darwin_160`    |   3  | Apple macOS 10.12 "Sierra" (Intel 32)                 |
|  `x86_darwin_170`    |   3  | Apple macOS 10.13 "High Sierra" (Intel 32)            |
|  `x86_darwin_180`    |   3  | Apple macOS 10.14 "Mojave" (Intel 32)                 |
|  `x86_darwin_190`    |   3  | Apple macOS 10.15 "Catalina" (Intel 32)               |
|  `x86_darwin_80`     |   3  | Apple Mac OS X 10.4 "Tiger" (Intel 32)                |
|  `x86_darwin_90`     |   3  | Apple Mac OS X 10.5 "Leopard" (Intel 32/64)           |
|----------------------|------|-------------------------------------------------------|
