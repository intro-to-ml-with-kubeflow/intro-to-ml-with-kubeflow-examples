#!/bin/bash

# Check all the shell scripts
find ./ -iregex '^.+\.??sh$' -type f -print0 | xargs -0 shellcheck
