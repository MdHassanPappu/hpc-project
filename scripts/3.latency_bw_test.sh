#!/bin/bash

# need to install osu micro benchmarks with any method before using it.   

OUTPUT_FILE="$HOME/hpc-project/log/osu_placement_results.txt"
LAT_CSV="$HOME/hpc-project/log/latency_results.csv"
BW_CSV="$HOME/hpc-project/log/bandwidth_results.csv"


module load tools/numactl/2.0.16-GCCcore-13.2.0

# === Added Warmup and Iterations ===
WARMUP=10
ITERATIONS=1000

# CPU masks for intra-node placement 
declare -A CPU_MASKS=(
    [same_numa]="0x1,0x10"
    [diff_numa_same_socket]="0x1,0x10000"
    [diff_socket_same_node]="0x1,0x10000000000000000"
)

PLACEMENTS=("same_numa" "diff_numa_same_socket" "diff_socket_same_node" "inter_node")
BENCHMARKS=("osu_get_latency" "osu_get_bw")

#  benchmark path
find_binary_in_path() {
    local binary_name=$1
    which "$binary_name" 2>/dev/null
}

echo "==== OSU Placement Test Results ====" | tee "$OUTPUT_FILE"
echo "Date: $(date)" | tee -a "$OUTPUT_FILE"
echo "Nodes allocated: $(scontrol show hostname)" | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

echo "placement,size,latency_us" > "$LAT_CSV"
echo "placement,size,bandwidth_MBps" > "$BW_CSV"

for placement in "${PLACEMENTS[@]}"; do
    echo "---- Placement: $placement ----" | tee -a "$OUTPUT_FILE"

    if [[ "$placement" == "inter_node" ]]; then
        echo "Hardware topology (inter-node)" | tee -a "$OUTPUT_FILE"
        BIND_ARGS="--cpu-bind=cores"
        NODE_ARGS="--nodes=2"
    else
        echo "Hardware topology (intra-node)" | tee -a "$OUTPUT_FILE"
        BIND_ARGS="--cpu-bind=mask_cpu:${CPU_MASKS[$placement]}"
        NODE_ARGS="--nodes=1"
    fi

    srun $NODE_ARGS -n 2 $BIND_ARGS bash -c '
        CPU_LIST=$(taskset -cp $$ | awk -F: "{print \$2}" | tr -d " ")
        FIRST_CPU=$(echo $CPU_LIST | cut -d"," -f1)
        TOPOLOGY=$(lscpu -p=cpu,socket,node | grep "^$FIRST_CPU,")
        SOCKET=$(echo $TOPOLOGY | cut -d, -f2)
        NUMA=$(echo $TOPOLOGY | cut -d, -f3)
        NODE=$(hostname)
        echo "Task $SLURM_PROCID on Node $NODE: CPU(s) $CPU_LIST, Socket $SOCKET, NUMA node $NUMA"
    ' | tee -a "$OUTPUT_FILE"

    echo "" | tee -a "$OUTPUT_FILE"

    for bench in "${BENCHMARKS[@]}"; do
        bench_path=$(find_binary_in_path "$bench")

        if [[ -z "$bench_path" || ! -x "$bench_path" ]]; then
            echo "Benchmark not found: $bench" | tee -a "$OUTPUT_FILE"
            continue
        fi

        echo "Running $bench from $bench_path ..." | tee -a "$OUTPUT_FILE"

        TMP_OUT=$(mktemp)

        if [[ "$bench" == "osu_get_latency" ]]; then
            srun $NODE_ARGS -n 2 $BIND_ARGS "$bench_path" -m 8192 -x $WARMUP -i $ITERATIONS | tee -a "$OUTPUT_FILE" | tee "$TMP_OUT"
            grep -E '^[0-9]' "$TMP_OUT" | awk -v place="$placement" '{print place","$1","$2}' >> "$LAT_CSV"
        elif [[ "$bench" == "osu_get_bw" ]]; then
            srun $NODE_ARGS -n 2 $BIND_ARGS "$bench_path" -m 1048576 -x $WARMUP -i $ITERATIONS | tee -a "$OUTPUT_FILE" | tee "$TMP_OUT"
            grep -E '^[0-9]' "$TMP_OUT" | awk -v place="$placement" '{print place","$1","$2}' >> "$BW_CSV"
        else
            srun $NODE_ARGS -n 2 $BIND_ARGS "$bench_path" -x $WARMUP -i $ITERATIONS | tee -a "$OUTPUT_FILE"
        fi

        rm -f "$TMP_OUT"
        echo "" | tee -a "$OUTPUT_FILE"
    done

    echo "" | tee -a "$OUTPUT_FILE"
done

echo "==== Test Complete ====" | tee -a "$OUTPUT_FILE"
# echo "== results are stored in the log directory ==" | tee -a "$OUTPUT_FILE"
# echo "============================================" | tee -a "$OUTPUT_FILE"
echo "Log file: $HOME/hpc-project/log/" | tee -a "$OUTPUT_FILE"
