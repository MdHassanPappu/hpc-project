#!/bin/bash

# Set up log directory
LOG_DIR="$HOME/hpc-project/log"
mkdir -p "$LOG_DIR"

# Navigate to the test directory
cd "$EBROOTOSUMINMICROMINBENCHMARKS/libexec/osu-micro-benchmarks/mpi/one-sided/" || {
    echo "Directory not found: $EBROOTOSUMINMICROMINBENCHMARKS/libexec/osu-micro-benchmarks/mpi/one-sided/"
    exit 1
}

# Determine OSU install type
if [[ "$EBROOTOSUMINMICROMINBENCHMARKS" == *"EasyBuild"* ]]; then
    Type="EasyBuild"
elif [[ "$EBROOTOSUMINMICROMINBENCHMARKS" == *"eessi"* ]]; then
    Type="EESSI"
else
    Type="Local"
fi

LOG_FILE="$LOG_DIR/osu_test_results_${Type}.txt"
rm $LOG_FILE

# Function to log test output
log_test() {
    local test_name=$1
    local command=$2
    echo "Running $test_name" >> "$LOG_FILE"
    echo "Command: $command" >> "$LOG_FILE"
    echo "----------------------------------------" >> "$LOG_FILE"
    eval "$command" >> "$LOG_FILE" 2>&1
    echo "" >> "$LOG_FILE"
}

# List of tests to run (osu_get_latency and osu_get_bw)
BENCHMARKS=("osu_get_latency" "osu_get_bw")
for benchmark in "${BENCHMARKS[@]}"; do
    echo "===== Running $benchmark tests =====" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"

    # T1: Same core, SMT siblings
    log_test "T1: Same core, SMT siblings" "srun -N1 -n2 --cpu-bind=threads ./$benchmark"

    # T2: Same socket, different cores
    log_test "T2: Same socket, different cores" "srun -N1 -n2 --cpu-bind=cores ./$benchmark"

    # T3: Different sockets
    log_test "T3: Different sockets" "srun -N1 -n2 --cpu-bind=sockets ./$benchmark"

    # T4: Different NUMA domains
    log_test "T4: Different NUMA domains" "srun -N1 -n2 --cpu-bind=ldoms ./$benchmark"

    # T5: Max hop / farthest cores
    aff_output=$(srun -N1 -n2 bash -c 'taskset -pc $$' 2>/dev/null | grep "current affinity list")
    core_list=$(echo "$aff_output" | awk -F ':' '{print $2}' | tr -d ' ' | tr ',' '\n' | sort -n | uniq)
    min_id=$(echo "$core_list" | head -n1)
    max_id=$(echo "$core_list" | tail -n1)
    log_test "T4: Max hop / farthest cores ($min_id, $max_id)" "srun -N1 -n2 --cpu-bind=map_cpu:$min_id,$max_id ./$benchmark"

    # T6: Neighboring sockets (or fallback)
    mid1=$(echo "$core_list" | head -n2 | tail -n1)
    mid2=$(echo "$core_list" | head -n3 | tail -n1)
    distance=$(( mid2 - mid1 ))

    if [[ $distance -le 4 ]]; then
        t5_cpu1=$mid1
        t5_cpu2=$mid2
    else
        t5_cpu1=$min_id
        t5_cpu2=$mid1
    fi
    log_test "T5: Neighboring sockets ($t5_cpu1, $t5_cpu2)" "srun -N1 -n2 --cpu-bind=map_cpu:$t5_cpu1,$t5_cpu2 ./$benchmark"

    # T7: No binding
    log_test "T6: No binding" "srun -N1 -n2 --cpu-bind=None ./$benchmark"

    # T8: NUMA-aware placement (get NUMA node of min_id)
    numa_node=$(numactl --hardware | awk -v cid=$min_id '
        /node [0-9]+ cpus:/ {
            for (i=4; i<=NF; ++i) {
                if ($i == cid) {
                    match($0, /node ([0-9]+)/, m)
                    print m[1]
                    exit
                }
            }
        }
    ')

    if [[ -n "$numa_node" ]]; then
        log_test "T7: NUMA-aware placement (node $numa_node)" \
                "srun -N1 -n2 bash -c 'numactl --cpunodebind=$numa_node --membind=$numa_node ./$benchmark'"
    else
        echo "Warning: Could not determine NUMA node for CPU $min_id" >> "$LOG_FILE"
    fi
    
    # Check if multiple nodes are available in the allocation
    NODE_COUNT=$(scontrol show hostnames | wc -l)
    
    if [ "$NODE_COUNT" -ge 2 ]; then
	# T9: Basic Cross-Node Communication
        log_test "T8: Basic Cross-Node Communication" "srun -N2 -n2 --ntasks-per-node=1 ./$benchmark"

	# T10: Multi-Node with thread binding
        log_test "T10: Multi-Node with thread binding" "srun -N2 -n2 --ntasks-per-node=1 --cpu-bind=threads ./$benchmark"

        # T11: Multi-Node with socket binding
        log_test "T11: Multi-Node with socket binding" "srun -N2 -n2 --ntasks-per-node=1 --cpu-bind=sockets ./$benchmark"

        # T12: Multi-Node with core binding
        log_test "T12: Multi-Node with core binding" "srun -N2 -n2 --ntasks-per-node=1 --cpu-bind=cores ./$benchmark"

        # T13: Multi-Node with NUMA domain binding
        log_test "T13: Multi-Node with NUMA domain binding" "srun -N2 -n2 --ntasks-per-node=1 --cpu-bind=ldoms ./$benchmark"
    else
        echo "WARNING: Multi-node tests (T8-T13) skipped - need at least 2 nodes" >> "$LOG_FILE"
        echo "Current allocation has $NODE_COUNT node(s)" >> "$LOG_FILE"
        echo "" >> "$LOG_FILE"
    fi
done

echo "✅ Test run completed. Results saved to $LOG_FILE"
echo "To view results: less $LOG_FILE"

