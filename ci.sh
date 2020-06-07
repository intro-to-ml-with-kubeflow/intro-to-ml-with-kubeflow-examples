#!/bin/bash

set -ex

# Check all the shell scripts
find ./ -iregex '^.+\.sh$' -type f -print0 | xargs -0 shellcheck -e SC1091 -e SC2164 -e SC1090
# Check for cases where I use tags rather than tag
bad_tags=$(grep -r "tags::" ./ | grep -v "ci.sh:" || true)
# Look for long lines
long_lines=$(grep --include '*.sh' -Hnr '.\{90\}' ./ | grep -v "venv" || true)
if [[ -n "$bad_tags" ]]; then
  echo "Found bad tags $bad_tags replace tags with tag"
fi
if [[ -n "$long_lines" ]]; then
  print "Found long lines:\n$long_lines"
fi
if [[ -n "$bad_tags" ]] || [[ -n "$long_lines" ]]; then
  exit 1
fi
./runthrough.sh
