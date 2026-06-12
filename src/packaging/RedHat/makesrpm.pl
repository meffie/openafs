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
) or pod2usage(-exitval => 1, -verbose => 1);
pod2usage(-exitval => 0, -verbose => 1) if $help;
pod2usage(-exitval => 0, -verbose => 2, -noperldoc => 1) if $man;

my $srcball = shift;
my $relnotes = shift;
my $changelog = shift;
my $cellservdb = shift;

if (!defined($srcball)) {
    pod2usage(-exitval => 1, -verbose => 1);
}

if (! -f $srcball) {
    die "$progname: Source archive not found: $srcball\n";
}

if (!defined($tmpdir)) {
    $tmpdir = File::Temp::tempdir(CLEANUP => 1);
}
run_command("tar", "-C", $tmpdir, "-xvjf", $srcball, "--wildcards", "*/src/packaging/RedHat");
my ($packaging) = glob("$tmpdir/openafs-*/src/packaging/RedHat");
if (!defined($packaging)) {
    die "$progname: Unable to find RedHat packaging directory in '${srcball}'.\n";
}

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

# Determine the package Version and Release tags from the OpenAFS version.
# We need to handle a number of varieties of OpenAFS version formats:
# Normal: 1.7.0
# Prereleases: 1.7.0pre1
# Development trees: 1.7.0dev
# and RPMS which are built from trees midway between heads, such as
# 1.7.0-45-gabcdef or 1.7.0pre1-37-g12345 or 1.7.0dev-56-g98765

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

# Build the RPM root

File::Path::mkpath([ $tmpdir."/rpmdir/SPECS",
                     $tmpdir."/rpmdir/SRPMS",
                     $tmpdir."/rpmdir/SOURCES"], 0, 0755);

File::Copy::copy($srcball,
                 $tmpdir."/rpmdir/SOURCES/openafs-${openafs_version}-src.tar.bz2")
    or die "$progname: Unable to copy $srcball into position: $!\n";

# Populate it with all the stuff in the packaging directory, except the
# specfile
for my $packaging_file (glob("$packaging/*")) {
    my $file = File::Basename::fileparse($packaging_file);
    next if $file eq "openafs.spec.in";
    print "$progname: Copying $file into place\n";
    File::Copy::copy($packaging_file, "$tmpdir/rpmdir/SOURCES/$file")
        or die "$progname: Unable to copy $file into position: $!\n";
}

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

makesrpm.pl - Build the SRPM for OpenAFS from source distibution files

=head1 SYNOPSIS

makesrpm.pl [options] <src.tar.bz2> <doc.tar.bz2> [<relnotes> [<changelog> [<cellservdb>]]]

=head1 DESCRIPTION

Build the SRPM for OpenAFS from source distibution files. Generate empty RELNOTES
and ChangeLog files if not provided. Download the CellServDB file from
grand.central.org if one is not provided.

=head1 OPTIONS

=over 4

=item B<--help>

Print help message and exit.

=item B<--man>

Print full man page and exit.

=item B<--dir> I<path>

Place the generated SRPM file in I<path> instead of the current directory.

=item B<--cellservdb-url> I<URL>

The URL of the CellServDB file to be downloaded when B<cellservdb> is not
specified, and the URL to be set in the C<Source20> source directive in the
generated F<openafs.spec> RPM spec file.  When not specified, I<URL> is is read
from the F<openafs.spec.in> file extracted from the source archive.

=back

=cut
