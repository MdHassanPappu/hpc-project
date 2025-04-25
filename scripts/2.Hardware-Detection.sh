#!/bin/bash
# filepath: /home/users/bjiang/hpc-project/scripts/verify_placement.sh

# =====================================================
# Combined hardware detection and placement verification 
# =====================================================

# Setup environment
LOG_DIR="$HOME/hpc-project/log"
mkdir -p "$LOG_DIR"

# Function to detect hardware topology
detect_hardware_topology() {
    echo "===== Hardware Topology Detection ====="
    echo "Date: $(date)"
    echo ""
    
    # Basic hardware detection
    NUMA_COUNT=$(lscpu | grep "^NUMA node(s):" | awk '{print $3}')
    SOCKET_COUNT=$(lscpu | grep "^Socket(s):" | awk '{print $2}')
    CORE_COUNT=$(lscpu | grep "^Core(s) per socket:" | awk '{print $4}')
    THREAD_COUNT=$(lscpu | grep "^Thread(s) per core:" | awk '{print $4}')

    echo "Detected configuration:"
    echo "- $NUMA_COUNT NUMA node(s)"
    echo "- $SOCKET_COUNT socket(s)"
    echo "- $CORE_COUNT core(s) per socket"
    echo "- $THREAD_COUNT thread(s) per core"
    
    # Calculate NUMA nodes per socket
    NUMA_PER_SOCKET=$(( $NUMA_COUNT / $SOCKET_COUNT ))
    echo "- $NUMA_PER_SOCKET NUMA node(s) per socket"
    
    # Map NUMA nodes to sockets
    declare -A SOCKET_TO_NUMA
    echo "NUMA to socket mapping:"
    
    for n in $(seq 0 $((NUMA_COUNT-1))); do
        if numactl -H | grep -q "node $n"; then
            # Find a CPU in this NUMA node
            CPU=$(numactl -H | grep -A1 "node $n cpus:" | tail -1 | awk '{print $1}')
            if [ ! -z "$CPU" ]; then
                SOCKET=$(lscpu -p=cpu,socket | grep "^$CPU," | cut -d, -f2)
                echo "- NUMA node $n is on socket $SOCKET (detected via CPU $CPU)"
                
                # Build the mapping
                if [ -z "${SOCKET_TO_NUMA[$SOCKET]}" ]; then
                    SOCKET_TO_NUMA[$SOCKET]=$n
                else
                    SOCKET_TO_NUMA[$SOCKET]="${SOCKET_TO_NUMA[$SOCKET]} $n"
                fi
            fi
        fi
    done
    
    # Create arrays of NUMA nodes by socket
    SOCKET0_NUMAS=()
    SOCKET1_NUMAS=()
    if [ ! -z "${SOCKET_TO_NUMA[0]}" ]; then
        read -a SOCKET0_NUMAS <<< "${SOCKET_TO_NUMA[0]}"
    fi
    if [ ! -z "${SOCKET_TO_NUMA[1]}" ]; then
        read -a SOCKET1_NUMAS <<< "${SOCKET_TO_NUMA[1]}"
    fi
    
    echo "- NUMA nodes on socket 0: ${SOCKET0_NUMAS[*]:-none}"
    echo "- NUMA nodes on socket 1: ${SOCKET1_NUMAS[*]:-none}"
    
    # Detect if we have multiple NUMA per socket
    MULTI_NUMA_PER_SOCKET=0
    for s in "${!SOCKET_TO_NUMA[@]}"; do
        NUMA_COUNT_IN_SOCKET=$(echo "${SOCKET_TO_NUMA[$s]}" | wc -w)
        if [ "$NUMA_COUNT_IN_SOCKET" -gt 1 ]; then
            MULTI_NUMA_PER_SOCKET=1
            break
        fi
    done
    
    if [ "$MULTI_NUMA_PER_SOCKET" -eq 1 ]; then
        echo "- Multiple NUMA nodes per socket detected"
    else
        echo "- Single NUMA node per socket detected"
    fi
    
    # Recommended NUMA nodes for different placement scenarios
    echo ""
    echo "Recommended NUMA nodes for placement scenarios:"
    
    # For same_numa
    NUMA_SAME=0
    if [ ${#SOCKET0_NUMAS[@]} -gt 0 ]; then
        NUMA_SAME=${SOCKET0_NUMAS[0]}
    fi
    echo "- same_numa: NUMA node $NUMA_SAME"
    
    # For diff_numa_same_socket
    NUMA_DIFF_SAME_SOCKET_1=${SOCKET0_NUMAS[0]:-0}
    NUMA_DIFF_SAME_SOCKET_2=${SOCKET0_NUMAS[1]:-0}
    if [ "$MULTI_NUMA_PER_SOCKET" -eq 1 ] && [ ${#SOCKET0_NUMAS[@]} -gt 1 ]; then
        echo "- diff_numa_same_socket: NUMA nodes ${SOCKET0_NUMAS[0]} and ${SOCKET0_NUMAS[1]}"
    else
        echo "- diff_numa_same_socket: Not available (fallback to same NUMA)"
        if [ "$SOCKET_COUNT" -gt 1 ]; then
            echo "  Consider using diff_socket_same_node instead"
        fi
    fi
    
    # For diff_socket_same_node
    NUMA_DIFF_SOCKET_1=${SOCKET0_NUMAS[0]:-0}
    NUMA_DIFF_SOCKET_2=${SOCKET1_NUMAS[0]:-0}
    if [ ${#SOCKET0_NUMAS[@]} -gt 0 ] && [ ${#SOCKET1_NUMAS[@]} -gt 0 ]; then
        echo "- diff_socket_same_node: NUMA nodes $NUMA_DIFF_SOCKET_1 (socket 0) and $NUMA_DIFF_SOCKET_2 (socket 1)"
    else
        echo "- diff_socket_same_node: Not available (single socket system)"
    fi
    
    # Export variables for external use
    export NUMA_COUNT SOCKET_COUNT NUMA_PER_SOCKET MULTI_NUMA_PER_SOCKET
    export NUMA_SAME NUMA_DIFF_SAME_SOCKET_1 NUMA_DIFF_SAME_SOCKET_2
    export NUMA_DIFF_SOCKET_1 NUMA_DIFF_SOCKET_2
    
    echo ""
    echo "NUMA variables exported to environment"
    echo "====================================="
}

# Function to verify process placement for current process
verify_placement() {
    local task_id=${SLURM_PROCID:-0}
    echo "==== Task $task_id placement ===="
    echo "Running on host: $(hostname)"
    
    if command -v numactl >/dev/null 2>&1; then
        echo "NUMA binding: $(numactl --show 2>/dev/null | grep -E 'nodebind|membind')"
    else
        echo "NUMA binding: numactl not available"
    fi
    
    if command -v lscpu >/dev/null 2>&1; then
        CPUS=$(taskset -cp $$ 2>/dev/null | grep -o "[0-9,]*$")
        echo "CPUs: $CPUS"
        
        # Get first CPU in the mask for node detection
        FIRST_CPU=$(echo $CPUS | cut -d, -f1)
        
        SOCKET=$(lscpu -p=cpu,socket | grep -E "(^|,)$FIRST_CPU(,|$)" | cut -d, -f2 | head -1)
        echo "Socket: $SOCKET"
        
        NUMA=$(lscpu -p=cpu,node | grep -E "(^|,)$FIRST_CPU(,|$)" | cut -d, -f2 | head -1)
        echo "NUMA node: $NUMA"
        
        # Additional CPU info
        CORE=$(lscpu -p=cpu,core | grep -E "(^|,)$FIRST_CPU(,|$)" | cut -d, -f2 | head -1)
        echo "Core: $CORE"
    else
        echo "CPU mapping: lscpu not available"
    fi
    
    echo "============================"
}

# Generate placement helper script
generate_placement_scripts() {
    echo "Generating placement helper scripts..."
    
    # Script for binding to the same NUMA node
    cat > $LOG_DIR/bind_same_numa.sh << EOF
#!/bin/bash
# Bind both processes to the same NUMA node
numactl --cpunodebind=$NUMA_SAME --membind=$NUMA_SAME \$@
EOF
    chmod +x $LOG_DIR/bind_same_numa.sh
    
    # Script for binding to different NUMA nodes on same socket
    cat > $LOG_DIR/bind_diff_numa_same_socket.sh << EOF
#!/bin/bash
# Bind processes to different NUMA nodes on the same socket
if [ "\$SLURM_PROCID" = "0" ]; then
    numactl --cpunodebind=$NUMA_DIFF_SAME_SOCKET_1 --membind=$NUMA_DIFF_SAME_SOCKET_1 \$@
else
    numactl --cpunodebind=$NUMA_DIFF_SAME_SOCKET_2 --membind=$NUMA_DIFF_SAME_SOCKET_2 \$@
fi
EOF
    chmod +x $LOG_DIR/bind_diff_numa_same_socket.sh
    
    # Script for binding to different sockets
    cat > $LOG_DIR/bind_diff_socket.sh << EOF
#!/bin/bash
# Bind processes to different sockets
if [ "\$SLURM_PROCID" = "0" ]; then
    numactl --cpunodebind=$NUMA_DIFF_SOCKET_1 --membind=$NUMA_DIFF_SOCKET_1 \$@
else
    numactl --cpunodebind=$NUMA_DIFF_SOCKET_2 --membind=$NUMA_DIFF_SOCKET_2 \$@
fi
EOF
    chmod +x $LOG_DIR/bind_diff_socket.sh
    
    echo "Helper scripts generated in $LOG_DIR:"
    echo "- bind_same_numa.sh: Bind tasks to the same NUMA node"
    echo "- bind_diff_numa_same_socket.sh: Bind tasks to different NUMA nodes on same socket"
    echo "- bind_diff_socket.sh: Bind tasks to different sockets"
}

# Main function
main() {
    # If running under Slurm, just verify placement
    if [ -n "$SLURM_PROCID" ]; then
        verify_placement
        return
    fi
    
    # Otherwise run full detection
    detect_hardware_topology
    
    # If requested, generate helper scripts
    if [ "$1" = "--generate-scripts" ]; then
        generate_placement_scripts
    fi
    
    # Always verify current process placement
    echo ""
    echo "Current process placement:"
    verify_placement
}

# Run main function with command line arguments
main "$@"