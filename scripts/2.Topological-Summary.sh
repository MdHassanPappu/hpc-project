#!/bin/bash

module load system/hwloc

OUTPUT_DIR="$HOME/hpc-project/log"
mkdir -p "$OUTPUT_DIR"
CSV_FILE="$OUTPUT_DIR/hw_topology_$(hostname).csv"

LSTOPOTXT=$(mktemp)
lstopo --no-io --of txt > "$LSTOPOTXT"

HOSTNAME=$(hostname)

# Extract socket (Package) IDs - fixed to capture all packages
SOCKET_IDS=$(grep -o "Package L#[0-9]*" "$LSTOPOTXT" | sed 's/Package L#//')
SOCKET_COUNT=$(echo "$SOCKET_IDS" | wc -l)
# Format socket IDs with proper prefix
SOCKET_LABELS=""
for id in $SOCKET_IDS; do
    SOCKET_LABELS="${SOCKET_LABELS}Package L#$id, "
done
SOCKET_LABELS=$(echo "$SOCKET_LABELS" | sed 's/, $//')

# Extract NUMA Node IDs - fixed to capture all NUMA nodes
NUMA_IDS=$(grep -o "NUMANode L#[0-9]*" "$LSTOPOTXT" | sed 's/NUMANode L#//')
NUMA_COUNT=$(echo "$NUMA_IDS" | wc -l)
# Format NUMA IDs with proper prefix
NUMA_LABELS=""
for id in $NUMA_IDS; do
    NUMA_LABELS="${NUMA_LABELS}L#$id, "
done
NUMA_LABELS=$(echo "$NUMA_LABELS" | sed 's/, $//')

# CPU core list from srun
aff_output=$(srun -N1 -n2 bash -c 'taskset -pc $$' 2>/dev/null | grep "current affinity list")
core_list=$(echo "$aff_output" | awk -F ':' '{print $2}' | tr -d ' ' | tr ',' '\n' | sort -n | uniq)
core_ids_csv=$(echo "$core_list" | tr '\n' ',' | sed 's/,/, /g' | sed 's/, $//')

# NUMA mapping of CPU cores
numa_node_list=()
for cid in $core_list; do
    nid=$(numactl --hardware | awk -v cid=$cid '
        /node [0-9]+ cpus:/ {
            for (i=4; i<=NF; ++i) {
                if ($i == cid) {
                    match($0, /node ([0-9]+)/, m)
                    print m[1]
                    exit
                }
            }
        }')
    [ -n "$nid" ] && numa_node_list+=("$nid")
done
unique_numa_nodes=$(echo "${numa_node_list[@]}" | tr ' ' '\n' | sort -n | uniq | tr '\n' ',' | sed 's/,/, /g' | sed 's/, $//')

# Memory per NUMA node - improved extraction
NUMA_MEMS=$(grep "NUMANode L#" "$LSTOPOTXT" | grep -o "[0-9]\+GB" | sed 's/GB//')
NUMA_MEM_MIN=$(echo "$NUMA_MEMS" | sort -n | head -1)
NUMA_MEM_MAX=$(echo "$NUMA_MEMS" | sort -nr | head -1)
if [ -n "$NUMA_MEM_MIN" ] && [ -n "$NUMA_MEM_MAX" ]; then
    if [ "$NUMA_MEM_MIN" = "$NUMA_MEM_MAX" ]; then
        mem_per_node_formatted="${NUMA_MEM_MIN} GB"
    else
        mem_per_node_formatted="${NUMA_MEM_MIN}–${NUMA_MEM_MAX} GB"
    fi
else
    mem_per_node_formatted="Unknown"
fi

# Total memory
total_mem_gb=$(grep "Machine" "$LSTOPOTXT" | grep -o "[0-9]\+GB" | head -1 | sed 's/GB//')
[ -z "$total_mem_gb" ] && total_mem_gb="Unknown"

# Cores and Threads
CORES_PER_SOCKET=$(lscpu | awk -F: '/Core\(s\) per socket/ {gsub(/ /,"",$2); print $2}')
THREADS_PER_CORE=$(lscpu | awk -F: '/Thread\(s\) per core/ {gsub(/ /,"",$2); print $2}')
TOTAL_CORES=$((CORES_PER_SOCKET * SOCKET_COUNT))
TOTAL_PUS=$((TOTAL_CORES * THREADS_PER_CORE))

# Caches - use lscpu for more reliable information
L1d=$(lscpu | awk -F: '/L1d cache:/ {print $2}' | tr -d ' ')
L1i=$(lscpu | awk -F: '/L1i cache:/ {print $2}' | tr -d ' ')
L2=$(lscpu | awk -F: '/L2 cache:/ {print $2}' | tr -d ' ')
L3=$(lscpu | awk -F: '/L3 cache:/ {print $2}' | tr -d ' ')

# Process L1 total size safely
L1d_size=$(echo "$L1d" | grep -o "[0-9]\+" || echo "0")
L1i_size=$(echo "$L1i" | grep -o "[0-9]\+" || echo "0") 
L1_total="${L1d_size}${L1d: -1}"

if [ "$L1d" != "" ] && [ "$L1i" != "" ]; then
    L1_total_size=$((L1d_size + L1i_size))
    L1_total="${L1_total_size}${L1d: -1}"
fi

# Output
{
echo "|Level|Entity|Count|"
echo "|---|---|---|"
echo "|**Node**|\`$HOSTNAME\`|1|"
echo "|**Physical Sockets**|\`$SOCKET_LABELS\`|$SOCKET_COUNT|"
echo "|**NUMA Nodes**|\`$NUMA_LABELS\` [NUMA Node $unique_numa_nodes are available]|$NUMA_COUNT (1 per socket)|"
echo "|**Cores per NUMA**|$CORES_PER_SOCKET (Core(s) per socket) [CPU ID $core_ids_csv are available]|$TOTAL_CORES total ($NUMA_COUNT NUMA × $CORES_PER_SOCKET cores)|"
echo "|**Threads per Core**|$THREADS_PER_CORE (PU per core)|$TOTAL_PUS Processing Units (PUs) total|"
echo "|**Memory per NUMA**|~$mem_per_node_formatted|~$total_mem_gb GB total (reported by \`lstopo\`)|"
echo "|**L3 Cache**|One L3 per socket ($L3 each)|$SOCKET_COUNT × $L3|"
echo "|**L2/L1 Caches**|$L2 L2 and $L1_total L1 ($L1d d + $L1i i) per core|$TOTAL_CORES of each|"
} > "$CSV_FILE"

rm "$LSTOPOTXT"
echo "✅ Hardware topology written to: $CSV_FILE"
