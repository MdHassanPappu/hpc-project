#!/bin/bash

# Default parameters
PARTITION="interactive"
QOS="debug"
TIME="2:00:00"
NODES=1
TASKS=32
CPUS=1
X11_FLAG=""

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --partition) PARTITION="$2"; shift 2 ;;
        --qos) QOS="$2"; shift 2 ;;
        --time) TIME="$2"; shift 2 ;;
        --nodes) NODES="$2"; shift 2 ;;
        --tasks) TASKS="$2"; shift 2 ;;
        --cpus) CPUS="$2"; shift 2 ;;
        --x11) X11_FLAG="--x11"; shift ;;  # No parameter needed
        *)
            echo "Unknown parameter: $1"
            exit 1
            ;;
    esac
done

# Execute salloc with given or default options
salloc -p "$PARTITION" --qos "$QOS" --time="$TIME" -N "$NODES" -n "$TASKS" -c "$CPUS" $X11_FLAG

