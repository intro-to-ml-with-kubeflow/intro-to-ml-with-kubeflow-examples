#!/bin/bash
cecho(){
    # shellcheck disable=SC2034
    RED='\033[0;31m'
    # shellcheck disable=SC2034
    GREEN='\033[0;32m'
    # shellcheck disable=SC2034
    YELLOW='\033[1;33m'
    # ... ADD MORE COLORS
    NC='\033[0m' # No Color

    printf "%s%s %s\\n" "${!1}" "${2}" "${NC}"
}
