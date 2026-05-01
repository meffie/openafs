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

# Globals
my $progname = "makesrpm";
my $tmpdir;

# Options
my $help = 0;
my $man = 0;
my $dir = ".";
my $cellservdb_url;
my $srcball;
my $docball;
my $relnotes;
my $changelog;
my $cellservdb;

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

GetOptions(
    "help|?" => \$help,
    "man" => \$man,
    "dir=s" => \$dir,
    "cellservdb-url=s" => \$cellservdb_url,
    "source=s" => \$srcball,
    "doc=s" => \$docball,
    "relnotes=s" => \$relnotes,
    "changelog=s" => \$changelog,
    "cellservdb=s" => \$cellservdb,
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
    pod2usage(-exitval => 1, -verbose => 0, -message => "--source is required");
}

if (! -f $srcball) {
    die "$progname: Source archive not found: $srcball\n";
}

#
# Create the RPM build directories.
#
if (!defined($tmpdir)) {
    $tmpdir = File::Temp::tempdir(CLEANUP => 1);
}

File::Path::mkpath([ $tmpdir."/rpmdir/SPECS",
                     $tmpdir."/rpmdir/SRPMS",
                     $tmpdir."/rpmdir/SOURCES"], 0, 0755);

#
# Determine the OpenAFS version.
#
my $openafs_version;
my $package_version;
my $package_release;

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
if ($openafs_version =~ m/(.*)(pre[0-9]+)/) {
    $package_version = $1;
    $package_release = "0.$2";
} elsif ($openafs_version =~ m/(.*)dev/) {
    $package_version = $1;
    $package_release = "0.dev";
} else {
    $package_version = $openafs_version;
    $package_release = 1;
}

if ($openafs_version =~ m/(.*)-([0-9]+)-(g[a-f0-9]+)$/) {
    $package_version = $1 if ($package_version eq $openafs_version);
    $package_release .= ".$2.$3";
}

# Avoid illegal characters in RPM package version and release strings.
$package_version =~ s/-/_/g;
$package_release =~ s/-/_/g;

print "$progname: Package version is $package_version\n";
print "$progname: Package release is $package_release\n";

#
# Extract the packaging files.
#
if (!defined($tmpdir)) {
    $tmpdir = File::Temp::tempdir(CLEANUP => 1);
}
run_command("tar", "-C", $tmpdir, "-xvjf", $srcball, "--wildcards", "*/src/packaging/RedHat");
my ($packaging) = glob("$tmpdir/openafs-*/src/packaging/RedHat");
if (!defined($packaging)) {
    die "$progname: Unable to find RedHat packaging directory in '${srcball}'.\n";
}

#
# Inspect the spec file to determine the CellServDB URL.
#
my $spec_input = "$packaging/openafs.spec.in";
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
File::Copy::copy($srcball,
                 $tmpdir."/rpmdir/SOURCES/openafs-${openafs_version}-src.tar.bz2")
    or die "$progname: Unable to copy $srcball into position: $!\n";

# Copy the doc archive if specified.
if (defined($docball)) {
    File::Copy::copy($docball,
                     "$tmpdir/rpmdir/SOURCES/openafs-${openafs_version}-doc.tar.bz2")
        or die "$progname: Unable to copy $docball into position: $!\n";
}

for my $packaging_file (glob("$packaging/*")) {
    my $file = File::Basename::fileparse($packaging_file);
    next if $file eq "openafs.spec.in";
    print "$progname: Copying $file into place\n";
    File::Copy::copy($packaging_file, "$tmpdir/rpmdir/SOURCES/$file")
        or die "$progname: Unable to copy $file into position: $!\n";
}

if ($cellservdb) {
    my $filename = File::Basename::fileparse($cellservdb_url);
    my $dest = "$tmpdir/rpmdir/SOURCES/$filename";
    print "$progname: Copying $cellservdb to $dest\n";
    File::Copy::copy($cellservdb, "$dest")
        or die "$progname: Unable to copy $cellservdb to $dest: $!\n";
} else {
    print "$progname: Downloading $cellservdb_url\n";
    run_command("wget", "-P", "$tmpdir/rpmdir/SOURCES", $cellservdb_url);
}

if ($relnotes) {
    File::Copy::copy($relnotes,
                     $tmpdir."/rpmdir/SOURCES/RELNOTES-${openafs_version}")
        or die "$progname: Unable to copy $relnotes into position: $!\n";
} else {
    if (! -f "$tmpdir/rpmdir/SOURCES/RELNOTES-${openafs_version}") {
        print "$progname: WARNING: No release notes provided. Using empty file\n";
        create_file("$tmpdir/rpmdir/SOURCES/RELNOTES-${openafs_version}");
    }
}

if ($changelog) {
    File::Copy::copy($changelog,
                     $tmpdir."/rpmdir/SOURCES/ChangeLog")
        or die "$progname: Unable to copy $changelog into position: $!\n";
} else {
    if (! -f "$tmpdir/rpmdir/SOURCES/ChangeLog") {
        print "$progname: WARNING: No changelog provided. Using empty file\n";
        create_file("$tmpdir/rpmdir/SOURCES/ChangeLog");
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
my $spec_output = "$tmpdir/rpmdir/SPECS/openafs.spec";
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
open(my $rpmbuild, "-|",
     "rpmbuild", "-bs", "--nodeps",
     "--define", "dist %undefined",
     "--define", "build_modules 0",
     "--define", "_topdir $tmpdir/rpmdir",
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
if (defined($dir)) {
    if (!defined($srpm)) {
        die "$progname: Generated SRPM file not found.\n";
    }
    my $srpm_filename = File::Basename::fileparse($srpm);
    my $srpm_output = File::Spec->rel2abs("$dir/$srpm_filename");
    File::Path::make_path($dir);
    File::Copy::copy($srpm, $srpm_output)
        or die "$progname: Failed to copy '$srpm' to '$srpm_output': $!\n";
    print "$progname: SRPM is $srpm_output\n";
}

__END__

=head1 NAME

makesrpm - Build an OpenAFS SRPM for RHEL-family distributions

=head1 SYNOPSIS

B<makesrpm.pl> S<<< B<--source> I<FILE> >>>
               S<<< [B<--doc> I<FILE>] >>>
               S<<< [B<--relnotes> I<FILE>] >>>
               S<<< [B<--changelog> I<FILE>] >>>
               S<<< [B<--cellservdb> I<FILE>] >>>
               S<<< [B<--cellservdb-url> I<URL>] >>>
               S<<< [B<--dir> I<DIR>] >>>
               S<<< [B<--help> | B<--man>] >>>

=head1 DESCRIPTION

B<makesrpm> is a tool to build an OpenAFS SRPM file for RHEL and RHEL-derived
distributions.

B<makesrpm> will extract the spec file and packaging files from the source
archive.

=head1 OPTIONS

=over 4

=item B<--source> I<FILE>

Use the specified OpenAFS source archive I<FILE>.  The archive is copied into
the C<SOURCES> directory and renamed based on the OpenAFS version.

=item B<--doc> I<FILE>

Use the specified OpenAFS documentation archive I<FILE>. The archive is copied
into the C<SOURCES> directory and renamed based on the OpenAFS version.

=item B<--relnotes> I<FILE>

Use the specified release notes file I<FILE>. The file is copied into the
C<SOURCES> directory and renamed appropriately.  An empty release notes file is
created if this option is not provided.

=item B<--changelog> I<FILE>

Use the specified F<ChangeLog> file I<FILE>. The file is copied into the
C<SOURCES> directory and renamed to C<ChangeLog>.  An empty F<ChangeLog> file
is created if this option is not provided.

=item B<--cellservdb> I<FILE>

Use the specified F<CellServDB> file I<FILE>. The file is copied into the
C<SOURCES> directory and renamed to match the filename in the C<Source>
directive in the spec file. If this option is not provided, the F<CellServDB>
file is downloaded from the URL specified in the spec file.

=item B<--dir> I<DIR>

Place the generated SRPM file in I<DIR> instead of the current directory.

=item B<--cellservdb-url> I<URL>

Overrides the download URL for the F<CellServDB> file. The provided I<URL> is
written into the spec file and is used to download the file if a local copy is
not provided with B<--cellservdb>.

=item B<--help>

Print help message and exit.

=item B<--man>

Print full man page and exit.

=back

=head1 EXAMPLES

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
