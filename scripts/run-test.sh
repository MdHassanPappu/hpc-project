#!/bin/bash

rm -rf ./bind_*.sh 2>/dev/null || true

module purege

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