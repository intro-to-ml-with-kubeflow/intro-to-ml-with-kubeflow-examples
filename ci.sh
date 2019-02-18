#!/bin/bash

# Check all the shell scripts
find ./ -iregex '^.+\.??sh$' -type f -print0 | xargs -0 shellcheck

# Check for long lines
longlines=$(grep '.\{100\}' -r ./)

if [[ ! -z "$longlines" ]]; then
  echo "Error found lines longer than allowed. $longlines"
  exit 1
fi
