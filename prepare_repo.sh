#!/bin/bash

git filter-branch --index-filter 'git rm --cached -qr --ignore-unmatch -- . && git reset -q $GIT_COMMIT -- data _indicators _goals scripts' --prune-empty -- --all

git mv _indicators meta
