#!/bin/bash
cecho(){
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    # ... ADD MORE COLORS
    NC='\033[0m' # No Color

    printf "%s%s %s\\n" "${!1}" "${2}" "${NC}"
}
