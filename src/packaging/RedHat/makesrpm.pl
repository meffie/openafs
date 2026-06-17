#!/usr/bin/perl
#
# Build an SRPM for OpenAFS, given a src tarball, release notes,
# and ChangeLog.  See the documentation at the end of this file.
#

use strict;
use warnings;

use Getopt::Long;
use Pod::Usage;
use File::Path;
use File::Copy;
use File::Temp;
use File::Basename;
use File::Spec;
use Cwd qw(cwd);

# Globals
my $progname = "makesrpm";
my $tmpdir;
my $toplevel;
my $openafs_version;

# Options
my $help = 0;
my $man = 0;
my $output_dir = ".";
my $cellservdb_url;
my $srcball;
my $docball;
my $relnotes;
my $changelog;
my $cellservdb;
my $package_version;
my $package_release;
my $spec_input;
my $packaging;
my $topdir;
my $prepare_only = 0;

#
# Create an empty file.
#
# Arguments:
#   path - The path to the file to create.
#
# Dies on failure.
#
sub create_file {
    my ($path) = @_;
    open(my $fh, '>', $path) or die "$progname: Unable to open file '$path': $!\n";
    close $fh;
}

#
# Read the contents of a file.
#
# Arguments:
#   path - The path to the file to be read.
#
# Returns:
#   The file contents as a string without the trailing newline.
#
# Dies on failure.
#
sub read_file {
    my ($path) = @_;
    my $contents;

    open(my $fh, "<", $path) or die "$progname: Unable to open '$path': $!\n";
    {
        local $/;  # Slurp the whole output.
        $contents = <$fh>;
    }
    chomp $contents;
    close($fh);
    return $contents;
}

#
# Run a command and exit on error.
#
# Arguments:
#   args - command line arguments
#
# Dies with an error message if the command returns a non-zero exit code.
#
sub run_command {
    my @args = @_;

    if (system(@args) != 0) {
        my $exit_code = $? >> 8;
        my $signal = $? & 127;
        my $command = join(' ', @args);

        if ($? == -1) {
            die "$progname: Failed to execute '$command': $!\n";
        }
        if ($signal) {
            my $coredump = ($? & 128) ? " (core dumped)" : "";
            die "$progname: '$command' died with signal $signal$coredump\n";
        }
        die "$progname: '$command' exited with code $exit_code (status $?)\n";
    }
}

#
# Run a command and return the stdout as a string.
#
# Arguments:
#   args - command line arguments
#
# Dies with an error message if the command returns a non-zero exit code.
#
sub capture_output {
    my @args = @_;
    my $command = join(' ', @args);
    my $output;

    open(my $pipe, "-|", @args) or
      die "$progname: Unable to run '$command': $!\n";
    {
        local $/;  # Slurp the whole output.
        $output = <$pipe>;
    }
    chomp $output;
    if (!close($pipe)) {
        if ($!) {
            die "$progname: Failed to close pipe: $!\n";
        }
        my $exit_code = $? >> 8;
        my $signal = $? & 127;

        if ($signal) {
            my $coredump = ($? & 128) ? " (core dumped)" : "";
            die "$progname: '$command' died with signal $signal$coredump\n";
        }
        die "$progname: Command '$command' failed with exit code ${exit_code} (status $?)\n";
    }
    return $output;
}

GetOptions(
    "help|?" => \$help,
    "man" => \$man,
    "output-dir|dir=s" => \$output_dir,
    "cellservdb-url=s" => \$cellservdb_url,
    "source=s" => \$srcball,
    "doc=s" => \$docball,
    "relnotes=s" => \$relnotes,
    "changelog=s" => \$changelog,
    "cellservdb=s" => \$cellservdb,
    "package-version=s" => \$package_version,
    "package-release=s" => \$package_release,
    "spec=s" => \$spec_input,
    "packaging=s" => \$packaging,
    "rpm-build-dir|topdir=s" => \$topdir,
    "prepare-only" => \$prepare_only,
) or pod2usage(-exitval => 1, -verbose => 1);
pod2usage(-exitval => 0, -verbose => 1) if $help;
pod2usage(-exitval => 0, -verbose => 2, -noperldoc => 1) if $man;

#
# Process positional arguments.
#
# This script previously only supported positional arguments for the input
# files.  For compatibility, fallback to positional arguments when no conflicts
# are seen.
#
if (defined($srcball) && defined($ARGV[0])) {
    pod2usage(-exitval => 1, -verbose => 0,
              -message => "--source and positional argument 1 are exclusive");
}
if (defined($docball) && defined($ARGV[1])) {
    pod2usage(-exitval => 1, -verbose => 0,
              -message => "--doc and positional argument 2 are exclusive");
}
if (defined($relnotes) && defined($ARGV[2])) {
    pod2usage(-exitval => 1, -verbose => 0,
              -message => "--relnotes and positional argument 3 are exclusive");
}
if (defined($changelog)  && defined($ARGV[3])) {
    pod2usage(-exitval => 1, -verbose => 0,
              -message => "--changelog and positional argument 4 are exclusive");
}
if (defined($cellservdb) && defined($ARGV[4])) {
    pod2usage(-exitval => 1, -verbose => 0,
              -message => "--cellservdb and positional argument 5 are exclusive");
}

$srcball    = $ARGV[0] if !defined($srcball)    && defined($ARGV[0]);
$docball    = $ARGV[1] if !defined($docball)    && defined($ARGV[1]);
$relnotes   = $ARGV[2] if !defined($relnotes)   && defined($ARGV[2]);
$changelog  = $ARGV[3] if !defined($changelog)  && defined($ARGV[3]);
$cellservdb = $ARGV[4] if !defined($cellservdb) && defined($ARGV[4]);

if (!defined($srcball)) {
    $toplevel = capture_output("git", "rev-parse", "--show-toplevel");
    if (!defined($toplevel)) {
        die "$progname: Unable to to find git top-level directory.\n";
    }
} else {
    if (! -f $srcball) {
        die "$progname: Source archive not found: $srcball\n";
    }
}

#
# Create the RPM build directories.
#
if (!defined($topdir)) {
    if ($prepare_only) {
        $topdir = capture_output("rpm", "--eval", "%{_topdir}");
    } else {
        if (!defined($tmpdir)) {
            $tmpdir = File::Temp::tempdir(CLEANUP => 1);
        }
        $topdir = "$tmpdir/rpmdir";
    }
}

File::Path::mkpath(["$topdir/SPECS",
                    "$topdir/SRPMS",
                    "$topdir/SOURCES"], 0, 0755);

#
# Determine the OpenAFS version.
#
if (!defined($srcball)) {
    $openafs_version = capture_output("$toplevel/build-tools/git-version", $toplevel);
    if ($openafs_version =~ /-dirty$/) {
        die "$progname: You have uncommitted changes. Please commit or stash them.\n";
    }
} else {
    if (!defined($tmpdir)) {
        $tmpdir = File::Temp::tempdir(CLEANUP => 1);
    }
    run_command("tar", "-C", $tmpdir, "-xvjf", $srcball, "--wildcards", "*/.version");
    my ($dot_version) = glob("$tmpdir/openafs-*/.version");
    if (!defined($dot_version)) {
        die "$progname: Unable to find '.version' in '${srcball}'.\n";
    }
    $openafs_version = read_file($dot_version);
    $openafs_version =~ s/openafs-[^-]*-//;
    $openafs_version =~ s/_/./g;
}
print "$progname: Building version $openafs_version\n";

#
# Determine the package Version and Release tags.
#
# We need to handle a number of varieties of OpenAFS version formats:
# Normal: 1.7.0
# Prereleases: 1.7.0pre1
# Development trees: 1.7.0dev
# and RPMS which are built from trees midway between heads, such as
# 1.7.0-45-gabcdef or 1.7.0pre1-37-g12345 or 1.7.0dev-56-g98765
#
if (!defined($package_version) || !defined($package_release)) {
    my ($pv, $pr);

    if ($openafs_version =~ m/(.*)(pre[0-9]+)/) {
        $pv = $1;
        $pr = "0.$2";
    } elsif ($openafs_version =~ m/(.*)dev/) {
        $pv = $1;
        $pr = "0.dev";
    } else {
        $pv = $openafs_version;
        $pr = 1;
    }

    if ($openafs_version =~ m/(.*)-([0-9]+)-(g[a-f0-9]+)$/) {
        $pv = $1 if ($pv eq $openafs_version);
        $pr .= ".$2.$3";
    }

    # Avoid illegal characters in RPM package version and release strings.
    $pv =~ s/-/_/g;
    $pr =~ s/-/_/g;

    if (!defined($package_version)) {
        $package_version = $pv;
    }
    if (!defined($package_release)) {
        $package_release = $pr;
    }
}
print "$progname: Package version is $package_version\n";
print "$progname: Package release is $package_release\n";

#
# Determine path to the packaging files.
#
if (!defined($packaging)) {
    if (!defined($srcball)) {
        $packaging = "$toplevel/src/packaging/RedHat";
    } else {
        if (!defined($tmpdir)) {
            $tmpdir = File::Temp::tempdir(CLEANUP => 1);
        }
        run_command("tar", "-C", $tmpdir, "-xvjf", $srcball, "--wildcards",
                    "*/src/packaging/RedHat");
        ($packaging) = glob("$tmpdir/openafs-*/src/packaging/RedHat");
        if (!defined($packaging)) {
            die "$progname: Unable to find RedHat packaging directory in '${srcball}'.\n";
        }
    }
}
print "$progname: Using packaging files in $packaging\n";

#
# Inspect the spec file to determine the CellServDB URL.
#
if (!defined($spec_input)) {
    $spec_input = "$packaging/SPECS/openafs.spec";
    if (! -f $spec_input) {
        $spec_input = "$packaging/openafs.spec.in";
    }
    if (! -f $spec_input) {
        die "$progname: Unable to find spec input file in '$packaging'\n";
    }
}

my $cellservdb_change_source;
if ($cellservdb_url) {
    $cellservdb_change_source = 1;  # Change the CellServDB source value in the spec.
} else {
    # Extract the CellServDB source URL from the input spec file.
    open(my $fh, $spec_input) or die "$progname: Unable to open $spec_input: $!\n";
    while (<$fh>) {
        if (/^Source20:\s*(.*)\s*$/) {
            $cellservdb_url = $1;
            last;
        }
    }
    close($fh);
    if (not $cellservdb_url) {
        die "$progname: Unable to find CellServDB source directive in $spec_input\n";
    }
    $cellservdb_change_source = 0;
}

#
# Populate the SOURCES directory.
#
if (!defined($srcball)) {
    my $cwd = cwd();
    chdir($toplevel) or die "$progname: Failed to cd to '$toplevel': $!";
    print "$progname: Creating source archive.\n";
    run_command("./build-tools/make-release",
                "--no-doc-tarball",
                "--dir", "$topdir/SOURCES",
                "HEAD");
    chdir($cwd) or die "$progname: Failed to cd to '$cwd': $!";
} else {
    File::Copy::copy($srcball,
                     "$topdir/SOURCES/openafs-${openafs_version}-src.tar.bz2")
        or die "$progname: Unable to copy $srcball into position: $!\n";
}

# Copy the doc archive if specified.
if (defined($docball)) {
    File::Copy::copy($docball,
                     "$topdir/SOURCES/openafs-${openafs_version}-doc.tar.bz2")
        or die "$progname: Unable to copy $docball into position: $!\n";
}

for my $packaging_file (glob("$packaging/* $packaging/SOURCES/*")) {
    next if -d $packaging_file;   # Skip directories
    my $file = File::Basename::fileparse($packaging_file);
    next if $file eq "openafs.spec.in";   # Skip spec template
    next if $file eq "openafs.spec";      # Skip spec file
    print "$progname: Copying $file into place\n";
    File::Copy::copy($packaging_file, "$topdir/SOURCES/$file")
        or die "$progname: Unable to copy $file into position: $!\n";
}

my $cellservdb_filename = File::Basename::fileparse($cellservdb_url);
if ($cellservdb) {
    my $dest = "$topdir/SOURCES/$cellservdb_filename";
    print "$progname: Copying $cellservdb to $dest\n";
    File::Copy::copy($cellservdb, "$dest")
        or die "$progname: Unable to copy $cellservdb to $dest: $!\n";
} else {
    if (! -f "$topdir/SOURCES/$cellservdb_filename") {
        print "$progname: Downloading $cellservdb_url\n";
        run_command("wget", "-P", "$topdir/SOURCES", $cellservdb_url);
    }
}

if ($relnotes) {
    File::Copy::copy($relnotes,
                     "$topdir/SOURCES/RELNOTES-${openafs_version}")
        or die "$progname: Unable to copy $relnotes into position: $!\n";
} else {
    if (! -f "$topdir/SOURCES/RELNOTES-${openafs_version}") {
        print "$progname: WARNING: No release notes provided. Using empty file\n";
        create_file("$topdir/SOURCES/RELNOTES-${openafs_version}");
    }
}

if ($changelog) {
    File::Copy::copy($changelog,
                     "$topdir/SOURCES/ChangeLog")
        or die "$progname: Unable to copy $changelog into position: $!\n";
} else {
    if (! -f "$topdir/SOURCES/ChangeLog") {
        print "$progname: WARNING: No changelog provided. Using empty file\n";
        create_file("$topdir/SOURCES/ChangeLog");
    }
}

#
# Populate the SPECS directory.
#
# Bake-in the OpenAFS version, the RPM Version, and RPM Release in the SRPM.
# This creates a SRPM that can build binary RPM files with the correct version
# information when running `rpmbuild --rebuild`.
#
# Also change the CellServDB source when a custom value is specified with the
# --cellservdb_url option.
#
my $spec_output = "$topdir/SPECS/openafs.spec";
open(my $in_fh, '<', $spec_input)
  or die "$progname: Cannot open input spec file '$spec_input': $!";
open(my $out_fh, '>', $spec_output)
  or die "$progname: Cannot open output spec file '$spec_output': $!";

while (<$in_fh>) {
    s/^\%define afsvers.*/%define afsvers $openafs_version/g;
    s/^\%define pkgvers.*/%define pkgvers $package_version/g;
    s/^\%define pkgrel.*/%define pkgrel $package_release/g;

    s/\@PACKAGE_VERSION\@/$openafs_version/g;
    s/\@LINUX_PKGVER\@/$package_version/g;
    s/\@LINUX_PKGREL\@/$package_release/g;

    if ($cellservdb_change_source) {
        s%^Source20:.*%Source20: $cellservdb_url%;
    }
    print $out_fh $_;
}
close $out_fh;
close $in_fh;

#
# Build the SRPM.
#
my $srpm;
my $abs_topdir = File::Spec->rel2abs($topdir);

if ($prepare_only) {
    print "$progname: RPM build directories prepared in '$abs_topdir'\n";
    print "$progname: SRPM build skipped (--prepare-only specified)\n";
    print "$progname: To build packages, run:\n";
    print "$progname:   rpmbuild -ba --define '_topdir $abs_topdir' $spec_output\n";
    exit 0;
}

open(my $rpmbuild, "-|",
     "rpmbuild", "-bs", "--nodeps",
     "--define", "dist %undefined",
     "--define", "build_modules 0",
     "--define", "_topdir $abs_topdir",
     $spec_output)
    or die "$progname: Failed to start rpmbuild: $!\n";
while (<$rpmbuild>) {
    print $_;
    if (/^Wrote: (.*)/) {
        $srpm = $1;
    }
}
if (!close($rpmbuild)) {
    if ($!) {
        die "$progname: Failed to close rpmbuild pipe: $!\n";
    }
    my $exit_code = $? >> 8;
    die "$progname: rpmbuild failed with exit code ${exit_code} (status $?)\n";
}

# Copy it out to somewhere useful.
if (defined($output_dir)) {
    if (!defined($srpm)) {
        die "$progname: Generated SRPM file not found.\n";
    }
    my $srpm_filename = File::Basename::fileparse($srpm);
    my $srpm_output = File::Spec->rel2abs("$output_dir/$srpm_filename");
    File::Path::make_path($output_dir);
    File::Copy::copy($srpm, $srpm_output)
        or die "$progname: Failed to copy '$srpm' to '$srpm_output': $!\n";
    print "$progname: SRPM is $srpm_output\n";
}

__END__

=head1 NAME

makesrpm - Build an OpenAFS SRPM for RHEL-family distributions

=head1 SYNOPSIS

B<makesrpm.pl> S<<< [B<--source> I<FILE>] >>>
               S<<< [B<--doc> I<FILE>] >>>
               S<<< [B<--relnotes> I<FILE>] >>>
               S<<< [B<--changelog> I<FILE>] >>>
               S<<< [B<--cellservdb> I<FILE>] >>>
               S<<< [B<--cellservdb-url> I<URL>] >>>
               S<<< [B<--output-dir> I<DIR>] >>>
               S<<< [B<--package-version> I<VERSION>] >>>
               S<<< [B<--package-release> I<RELEASE>] >>>
               S<<< [B<--packaging> I<DIR>] >>>
               S<<< [B<--spec> I<FILE>] >>>
               S<<< [B<--rpm-build-dir> I<DIR>] >>>
               S<<< [B<--prepare-only>] >>>
               S<<< [B<--help> | B<--man>] >>>

=head1 DESCRIPTION

B<makesrpm> is a tool to build an OpenAFS SRPM file for RHEL and RHEL-derived
distributions. It can build the SRPM from either a local git repository or an
source distribution archive.

When run without any options from within an OpenAFS local git repository,
B<makesrpm> will build a source archive from the current C<HEAD> commit and
then build the SRPM using the spec file and packaging files located in the
F<src/packaging/RedHat> directory in the source tree.  By default, B<makesrpm>
will refuse to build the source archive when uncommitted changes are detected
in local git repository.

When run with the B<--source> option, B<makesrpm> will extract the spec file
and packaging files from the source archive instead of the git working tree.

This tool can also prepare an RPM build directory for building OpenAFS RPM
packages instead of building an SRPM.  When run with the B<--prepare-only>
option, B<makesrpm> will create and populate RPM build directories instead of
building the SRPM. This allows you to inspect or modify the packaging files
before running B<rpmbuild> manually.

=head1 OPTIONS

=over 4

=item B<--source> I<FILE>

Use the specified OpenAFS source archive I<FILE>.  The archive is copied into
the C<SOURCES> directory and renamed based on the OpenAFS version. The
source archive is built from the current git commit when B<--source>
is not specified.

=item B<--doc> I<FILE>

Use the specified OpenAFS documentation archive I<FILE>. The archive is copied
into the C<SOURCES> directory and renamed based on the OpenAFS version.

=item B<--relnotes> I<FILE>

Use the specified release notes file I<FILE>. The file is copied into the
C<SOURCES> directory and renamed appropriately.  The release notes are
generated from the current git commit when B<--source> is not specified.  An
empty release notes file is created if this option is not provided and
B<--source> is specified.

=item B<--changelog> I<FILE>

Use the specified F<ChangeLog> file I<FILE>. The file is copied into the
C<SOURCES> directory and renamed to C<ChangeLog>.  The change log is generated
from the current git commit when B<--source> is not specified. An empty
F<ChangeLog> file is created if this option is not provided and B<--source> is
specified.

=item B<--cellservdb> I<FILE>

Use the specified F<CellServDB> file I<FILE>. The file is copied into the
C<SOURCES> directory and renamed to match the filename in the C<Source>
directive in the spec file. If this option is not provided, the F<CellServDB>
file is downloaded from the URL specified in the spec file.

=item B<--output-dir> I<DIR>, B<--dir> I<DIR>

Place the generated SRPM file in I<DIR> instead of the current directory.

=item B<--package-version> I<VERSION>

The package version string to be used for the package. This version is used for
the C<Version> tag in the spec file used to build the SRPM. When not specified,
the package version is derived from the OpenAFS version string.

=item B<--package-release> I<RELEASE>

The package release string to be used for the package. This release is used for
the C<Release> tag in the spec file used to build the SRPM. When not specified,
the package release is derived from the OpenAFS version string.

=item B<--packaging> I<DIR>

Specifies the directory containing the spec file and other packaging files.  If
this option is not specified, packaging file located in the F<src/packaging/RedHat>
directory in the local git repository are used.

If this option is not specified and the B<--source> option is specified, the
packaging files are extacted from the F<src/packaging/RedHat> directory from
the source archive.

=item B<--spec> I<FILE>

Specifies the path to the RPM spec file. If this option is not provided, the
spec file is located within the directory specified by B<--packaging>.

=item B<--cellservdb-url> I<URL>

Overrides the download URL for the F<CellServDB> file. The provided I<URL> is
written into the spec file and is used to download the file if a local copy is
not provided with B<--cellservdb>.

=item B<--rpm-build-dir> I<DIR>, B<--topdir> I<DIR>

Specifies the directory to use for the RPM build. The C<SPECS>, C<SOURCES>, and
C<SRPMS> subdirectories will be created in this directory.  If this option is
not provided, a temporary directory is used, which is automatically removed
when the script exits.

=item B<--prepare-only>

Prepare the rpmbuild SOURCE and SPECS directories with the packaging files, but
do not run C<rpmbuild> to build the SRPM.  The RPM build directories will be
created in the path specified by the B<--rpm-build-dir> option. If the
B<--rpm-build-dir> option is not specified, the default RPM build path will be
used (e.g., C<$HOME/rpmbuild>) instead of a temporary directory.

=item B<--help>

Print help message and exit.

=item B<--man>

Print full man page and exit.

=back

=head1 EXAMPLES

Build the SRPM from a git tag:

    $ git checkout openafs-stable-1_8_16
    $ ./src/packaging/RedHat/makesrpm.pl

Build the SRPM from a source distribution archive:

    $ makesrpm.pl --source openafs-1.9.0-src.tar.bz2

Build the SRPM from a source distribution archive with the given release notes
and change log:

    $ makesrpm.pl --source openafs-1.9.0-src.tar.bz2 \
                  --relnotes RELNOTES-1.9.0 \
                  --changelog ChangeLog

=head1 EXIT STATUS

B<makesrpm.pl> will exit with a status of 0 on success and a non-zero status on
failure.

=head1 SEE ALSO

L<rpmbuild(8)>, F<make-release>

=head1 AUTHOR

The original B<makesrpm.pl> was written by Simon Wilkinson <sxw@inf.ed.ac.uk>

=cut
