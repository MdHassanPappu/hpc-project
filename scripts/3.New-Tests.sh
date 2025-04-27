#!/bin/bash

# Set benchmark parameters as variables (like in ReFrame test)
LATENCY_SIZE=8192       # 8K bytes
BANDWIDTH_SIZE=1048576  # 1MB (1024*1024)
NUM_WARMUP_ITERS=10
NUM_ITERS=1000

# Set up log directory
LOG_DIR="$HOME/hpc-project/log"
SCRIPTS_DIR="$HOME/hpc-project/scripts"
mkdir -p "$LOG_DIR" 

module load tools/numactl/2.0.13-GCCcore-10.2.0 2>/dev/null || echo "Warning: numactl module not found"

echo "===== Hardware Detection ====="
echo "Detecting hardware topology..."
$SCRIPTS_DIR/2.Hardware-Detection.sh
echo "Generating binding scripts..."
$SCRIPTS_DIR/2.Hardware-Detection.sh --generate-scripts

# Verify binding scripts were generated
echo "Checking generated binding scripts:"
ls -la ./bind_*.sh || echo "Failed to generate binding scripts"
chmod 755 ./bind_*.sh 2>/dev/null || echo "No binding scripts to chmod"

# Create symlinks to the OSU benchmarks
OSU_DIR="$EBROOTOSUMINMICROMINBENCHMARKS/libexec/osu-micro-benchmarks/mpi/one-sided"
ln -sf "$OSU_DIR/osu_get_latency" .
ln -sf "$OSU_DIR/osu_get_bw" .

# Create log files for placement tests
PLACEMENT_LOG="$LOG_DIR/placement_tests.log"
CSV_LOG="$LOG_DIR/placement_results.csv"
rm -f "$PLACEMENT_LOG" "$CSV_LOG" 2>/dev/null || true
# CSV header
echo "timestamp,benchmark,placement_type,value,unit" > "$CSV_LOG"

# Function to run test and log results - matching ReFrame approach
run_placement_test() {
    local benchmark="$1"
    local placement="$2"
    local binding_script="$3"
    local slurm_options="$4"
    local log_file="$PLACEMENT_LOG"
    local size=$([ "$benchmark" == "get_latency" ] && echo $LATENCY_SIZE || echo $BANDWIDTH_SIZE)
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    
    echo "=================================================" >> "$log_file"
    echo "[$timestamp] Running $benchmark with $placement placement" >> "$log_file"
    echo "Using binding script: $binding_script" >> "$log_file"
    echo "Slurm options: $slurm_options" >> "$log_file"
    echo "Parameters: size=$size, warmup=$NUM_WARMUP_ITERS, iterations=$NUM_ITERS" >> "$log_file"
    echo "-------------------------------------------------" >> "$log_file"
    
    # Show CPU allocation for debugging
    srun $slurm_options -N1 -n2 bash -c 'echo "Available CPUs for this job: $(taskset -cp $$)"' >> "$log_file"

    # Run benchmark with output to temporary file
    if [ -n "$binding_script" ]; then
        srun $slurm_options --chdir="$PWD" ./$binding_script ./osu_$benchmark -m $size -x $NUM_WARMUP_ITERS -i $NUM_ITERS >> "$log_file"
    else
        srun $slurm_options --chdir="$PWD" ./osu_$benchmark -m $size -x $NUM_WARMUP_ITERS -i $NUM_ITERS >> "$log_file"
    fi
    # Run verification - exactly like ReFrame does
    echo "Placement verification:" >> "$log_file"
    srun -n2 ./hw-detect.sh --verify >> "$log_file"
    
    # Add to CSV
    echo "$timestamp,osu_$benchmark,$placement,$value,$unit" >> "$CSV_LOG"
    echo "" >> "$log_file"
    
    # Return the result for display
    echo "$value $unit"
}

# Main test execution with all placement types
echo "===== Starting Placement Tests =====" | tee -a "$PLACEMENT_LOG"
echo "Date: $(date)" | tee -a "$PLACEMENT_LOG"
echo "Test parameters: latency_size=$LATENCY_SIZE, bandwidth_size=$BANDWIDTH_SIZE" | tee -a "$PLACEMENT_LOG"
echo "                 warmup_iters=$NUM_WARMUP_ITERS, iters=$NUM_ITERS" | tee -a "$PLACEMENT_LOG"
echo "" | tee -a "$PLACEMENT_LOG"


# Same NUMA test
echo "Running same_numa test..." | tee -a "$PLACEMENT_LOG"
SAME_NUMA_OPTS="--nodes=1 --ntasks=2 --ntasks-per-node=2 --hint=nomultithread --distribution=block:block --cpu-bind=verbose numactl --show"
latency_result=$(run_placement_test "get_latency" "same_numa" "" "$SAME_NUMA_OPTS")
bandwidth_result=$(run_placement_test "get_bw" "same_numa" "" "$SAME_NUMA_OPTS")
printf "%-25s | %-15s | %-15s\n" "same_numa" "$latency_result" "$bandwidth_result" | tee -a "$PLACEMENT_LOG"

# Different NUMA, same socket test
echo "Running diff_numa_same_socket test..." | tee -a "$PLACEMENT_LOG"
DIFF_NUMA_OPTS="--nodes=1 --ntasks=2 --cpu-bind=ldom,verbose --hint=nomultithread --distribution=block:block numactl --show"
latency_result=$(run_placement_test "get_latency" "diff_numa_same_socket" "" "$DIFF_NUMA_OPTS")
bandwidth_result=$(run_placement_test "get_bw" "diff_numa_same_socket" "" "$DIFF_NUMA_OPTS")
printf "%-25s | %-15s | %-15s\n" "diff_numa_same_socket" "$latency_result" "$bandwidth_result" | tee -a "$PLACEMENT_LOG"

# Different socket, same node test
echo "Running diff_socket_same_node test..." | tee -a "$PLACEMENT_LOG"
DIFF_SOCKET_OPTS="--nodes=1 --ntasks=2 --ntasks-per-node=2 --sockets-per-node=2 --ntasks-per-socket=1 --cpu-bind=sockets,verbose --hint=nomultithread numactl --show"
latency_result=$(run_placement_test "get_latency" "diff_socket_same_node" "" "$DIFF_SOCKET_OPTS")
bandwidth_result=$(run_placement_test "get_bw" "diff_socket_same_node" "" "$DIFF_SOCKET_OPTS")
printf "%-25s | %-15s | %-15s\n" "diff_socket_same_node" "$latency_result" "$bandwidth_result" | tee -a "$PLACEMENT_LOG"

# Different node testd
echo "Running diff_node test..." | tee -a "$PLACEMENT_LOG"
DIFF_NODE_OPTS="--nodes=2 --ntasks=2 --ntasks-per-node=1 --distribution=cyclic numactl --show"
latency_result=$(run_placement_test "get_latency" "diff_node" "" "$DIFF_NODE_OPTS")
bandwidth_result=$(run_placement_test "get_bw" "diff_node" "" "$DIFF_NODE_OPTS")
printf "%-25s | %-15s | %-15s\n" "diff_node" "$latency_result" "$bandwidth_result" | tee -a "$PLACEMENT_LOG"


echo "" | tee -a "$PLACEMENT_LOG"
echo "✅ All placement tests completed." | tee -a "$PLACEMENT_LOG"
echo "Log file: $PLACEMENT_LOG" | tee -a "$PLACEMENT_LOG"
echo "CSV results: $CSV_LOG" | tee -a "$PLACEMENT_LOG"
echo "To view results: less $PLACEMENT_LOG"
