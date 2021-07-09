#!/bin/bash

set -e
set -x

REMOTE=meffie
git fetch $REMOTE
git branch -r | grep $REMOTE/bssize | sed 's@  meffie/@@' | while read b; do
  if ! git show-ref refs/heads/$b; then
    git branch --no-track $b $REMOTE/$b
  fi
done
