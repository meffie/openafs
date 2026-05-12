#!/bin/bash
#
# Create source archives for makesrpm.pl testing.
#

set -e
set -x

GIT_ROOT="`git rev-parse --show-toplevel`"
DATA_ROOT="${XDG_DATA_HOME:-$HOME/.local/share}/openafs/tests/makesrpm"

make_source_archive() {
    local version="$1"
    local commit="$2"
    local datadir="$DATA_ROOT/$version"

    mkdir -p "$datadir"
    (cd "$GIT_ROOT" && ./build-tools/make-release --dir "$datadir" "$commit")
    cp "$GIT_ROOT/src/afsd/CellServDB" "$datadir/CellServDB.2025-08-16"
    echo "dummy" > "$datadir/NEWS"
    echo "dummy" > "$datadir/RELNOTES-$version"
}

make_source_archive "1.8.15" "openafs-stable-1_8_15"
make_source_archive "1.8.16pre1" "openafs-stable-1_8_16pre1"
make_source_archive "master" "d5103c0d0e26091cd35cbd5f60fbc90c12578e00"  # A commit on the master branch
