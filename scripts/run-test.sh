#!/bin/bash

rm -rf ./bind_*.sh 2>/dev/null || true

module purege
module load devel/ReFrame/4.7.4-GCCcore-13.2.0

# Default method is local
METHOD="local"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --method|-m)
            METHOD="$2"
            shift 2
            ;;
        *)
            # Unknown option
            shift
            ;;
    esac
done

python main.py --$METHOD