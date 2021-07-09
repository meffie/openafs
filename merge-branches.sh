#!/bin/bash

set -e
set -x

INT=bssize/int
BRANCHES="
bssize/libadmin-xdr-allocated
bssize/bos-xdr-allocated
bssize/auth-userok-large-string-support
bssize/cmd-split
bssize/down-with-parseline
bssize/bosoprocs-allocate-strings-with-strdup
bssize/bozo-bosconfig-tests
bssize/bozo-overhaul-read-bozo-file
bssize/increase-bssize-to-4mb
bssize/bozo-safer-strings
"

git branch --no-track $INT bssize/base
git checkout $INT

for B in $BRANCHES; do
    git merge --no-ff -m "Merging $B into $INT" $B
done
