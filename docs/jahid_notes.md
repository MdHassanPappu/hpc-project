## SLURM Benchmarking: CPU Binding 
---

##  1. Allocate a Full Node Exclusively

```bash
salloc -N 1 -n 2 --exclusive
```

- Reserves 1 node entirely for your job.
- Gives access to all cores and memory on the node.

---

## 2. Inspect CPU and NUMA Topology.

```bash
lscpu | grep -E "Socket|NUMA|CPU"
```

---

##  3. Check Current Shell CPU Affinity

```bash
taskset -cp $$
```
## Setup environment

```bash
module load tools/numactl/2.0.16-GCCcore-13.2.0
```

---

### 🔸 Case 1: Intra-node – Same NUMA Node

```bash
srun -n 2 --cpu-bind=verbose,mask_cpu:0x3,0xc numactl --show

srun -n 2 --cpu-bind=verbose,mask_cpu:0x3,0xc ./2.Hardware-Detection.sh

srun -n 2 --cpu-bind=verbose,mask_cpu:0x3,0xc osu_get_latency -m 8192:8192

srun -n 2 --cpu-bind=verbose,mask_cpu:0x3,0xc osu_get_bw -m 1048576:1048576
```
- Task 0 → CPU 0-1 (Numa node 0)  (Socket 0)  
- Task 1 → CPU 2-3 (Numa node 0)  (Socket 0)

### Ensuring mem-bind for same node 
```bash
srun -n 2 --cpu-bind=verbose,mask_cpu:0x3,0xc bash -c '
numactl --membind=0 numactl --show'

srun -n 2 --cpu-bind=verbose,mask_cpu:0x3,0xc bash -c '
numactl --membind=0 osu_get_latency'

srun -n 2 --cpu-bind=verbose,mask_cpu:0x3,0xc bash -c '
numactl --membind=0 osu_get_bw'
```
---

### 🔸 Case 2: Intra-node – Same Socket, Different NUMA Nodes 

```bash
srun -n 2 --cpu-bind=verbose,mask_cpu:0x3,0x30000 numactl --show

srun -n 2 --cpu-bind=verbose,mask_cpu:0x3,0x30000 ./2.Hardware-Detection.sh

srun -n 2 --cpu-bind=verbose,mask_cpu:0x3,0x30000 osu_get_latency -m 8192:8192

srun -n 2 --cpu-bind=verbose,mask_cpu:0x3,0x30000  osu_get_bw -m 1048576:1048576
```

- Task 0 → CPU 0-1 (Numa node 0)  (Socket 0)  
- Task 1 → CPU 16-17 (Numa node 1) (Socket 0)

---

### 🔸 Case 3: Intra-node – Different Sockets

```bash
srun -n 2 --cpu-bind=verbose,mask_cpu:0x3,0x30000000000000000 numactl --show

srun -n 2 --cpu-bind=verbose,mask_cpu:0x3,0x30000000000000000 ./2.Hardware-Detection.sh

srun -n 2 --cpu-bind=verbose,mask_cpu:0x3,0x30000000000000000 osu_get_latency -m 8192:8192 

srun -n 2 --cpu-bind=verbose,mask_cpu:0x3,0x30000000000000000 osu_get_bw -m 1048576:1048576
```

- Task 0 → CPU 0-1 (Numa node 0)  (Socket 0)  
- Task 1 → CPU 16-17 (Numa node 4) (Socket 1)

---

### 🔸 Case 4: Inter-node

```bash
salloc -N 2 --exclusive

module load tools/numactl/2.0.16-GCCcore-13.2.0

srun -n 2 -c 2 --cpu-bind=verbose,cores numactl --show

srun -n 2 -c 2 --cpu-bind=verbose,cores ./2.Hardware-Detection.sh
```

- Each task runs on a different node with 2 cpu cores per task. 


---


### This is just a simple scripts that i used for osu_benchmarks test locally. 


## Scripts for the test in locally 

- After installation of osu benchmarks i tried such way. 
 
```bash
#!/bin/bash

OUTPUT_FILE="osu_intranode_results.txt"
HARDWARE_DETECTION_SCRIPT="/home/users/mhassan/hpc-project/scripts/2.Hardware-Detection.sh"

# CPU masksbit for different placement 
declare -A CPU_MASKS=(
    [same_numa]="0x3,0xc"
    [diff_numa_same_socket]="0x3,0x30000"
    [diff_socket_same_node]="0x3,0x30000000000000000"
)

BENCHMARKS=("osu_get_latency" "osu_get_bw")

echo "==== OSU Intra-Node Placement Test Results ====" | tee "$OUTPUT_FILE"
echo "Node: $(hostname)" | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

find_binary_in_path() {
    local binary_name=$1
    which "$binary_name" 2>/dev/null
}

# Run  benchmarks
for placement in "${!CPU_MASKS[@]}"; do
    mask="${CPU_MASKS[$placement]}"
    
    echo "---- Placement: $placement ----" | tee -a "$OUTPUT_FILE"
    
    echo "Hardware topology for $placement" | tee -a "$OUTPUT_FILE"
    echo "----------------------------------------------------" | tee -a "$OUTPUT_FILE"
    srun -n 2 --cpu-bind=verbose,mask_cpu:$mask numactl --show | tee -a "$OUTPUT_FILE"
    echo "" | tee -a "$OUTPUT_FILE"
    
    for bench in "${BENCHMARKS[@]}"; do
        bench_path=$(find_binary_in_path "$bench")
        
        if [[ -z "$bench_path" || ! -x "$bench_path" ]]; then
            echo "Benchmark not found: $bench" | tee -a "$OUTPUT_FILE"
            continue
        fi
        
        echo "Running $bench from $bench_path ..." | tee -a "$OUTPUT_FILE"
        srun -n 2 --cpu-bind=verbose,mask_cpu:$mask "$bench_path" | tee -a "$OUTPUT_FILE"
        echo "" | tee -a "$OUTPUT_FILE"
    done
    echo "" | tee -a "$OUTPUT_FILE"
done

echo "==== Test Complete ====" | tee -a "$OUTPUT_FILE"

```
------------------------


### Issues i got with reframe test.  

>with reframe it perfertcy binded process for same numa node and different numa node. but not for 
> - diff_numa_same_socket binded to → same numa same socket 
>- diff_socket_same_node  binded to → same socket diff numa node 

- now i'm trying to fix these senario with reframe. 


#### Specially the bandwith  values are varies a lot. In each test i got different values ranging a  lot. and latency almost stable for each case except test in different node. 


## OSU Placement Test Summary

After setting reference values for bandwidth and latency, I ran 24 tests across different placement scenarios. Though two placement scenarios are not place correctly `diff_numa_same_socket`, `diff_socket_same_node`.I'm trying to fix them. 

Out of 24 tests:
-  **15 tests passed** 
-  **9 tests failed** 

Below is a detailed breakdown:

| #  | Binary Source | Test Type | Placement Type         | Status | Value        | Target      |
|----|---------------|-----------|-------------------------|--------|--------------|-------------|
|  1 | local         | bandwidth | same_numa               | FAIL   | 6291.89 MB/s | 8200 MB/s   |
|  2 | local         | bandwidth | diff_numa_same_socket   | FAIL   | 5695.74 MB/s | 8000 MB/s   |
|  3 | local         | bandwidth | diff_socket_same_node   | FAIL   | 8998.36 MB/s | 8000 MB/s   |
|  4 | local         | bandwidth | diff_node               | OK     | 11837.48 MB/s| 12000 MB/s  |
|  5 | local         | latency   | same_numa               | OK     | 0.22 us      | 0.21 us     |
|  6 | local         | latency   | diff_numa_same_socket   | FAIL   | 0.24 us      | 0.21 us     |
|  7 | local         | latency   | diff_socket_same_node   | OK     | 0.21 us      | 0.21 us     |
|  8 | local         | latency   | diff_node               | OK     | 4.33 us      | 4.0 us      |
|  9 | eessi         | bandwidth | same_numa               | FAIL   | 7561.57 MB/s | 7200 MB/s   |
| 10 | eessi         | bandwidth | diff_numa_same_socket   | OK     | 8232.75 MB/s | 8000 MB/s   |
| 11 | eessi         | bandwidth | diff_socket_same_node   | FAIL   | 9632.5 MB/s  | 8000 MB/s   |
| 12 | eessi         | bandwidth | diff_node               | OK     | 12292.31 MB/s| 12000 MB/s  |
| 13 | eessi         | latency   | same_numa               | OK     | 0.2 us       | 0.21 us     |
| 14 | eessi         | latency   | diff_numa_same_socket   | OK     | 0.2 us       | 0.21 us     |
| 15 | eessi         | latency   | diff_socket_same_node   | OK     | 0.2 us       | 0.21 us     |
| 16 | eessi         | latency   | diff_node               | OK     | 4.31 us      | 4.0 us      |
| 17 | easybuild     | bandwidth | same_numa               | FAIL   | 8504.48 MB/s | 8000 MB/s   |
| 18 | easybuild     | bandwidth | diff_numa_same_socket   | FAIL   | 8420.54 MB/s | 8000 MB/s   |
| 19 | easybuild     | bandwidth | diff_socket_same_node   | FAIL   | 9058.0 MB/s  | 8000 MB/s   |
| 20 | easybuild     | bandwidth | diff_node               | OK     | 12321.59 MB/s| 12000 MB/s  |
| 21 | easybuild     | latency   | same_numa               | OK     | 0.2 us       | 0.21 us     |
| 22 | easybuild     | latency   | diff_numa_same_socket   | OK     | 0.21 us      | 0.21 us     |
| 23 | easybuild     | latency   | diff_socket_same_node   | OK     | 0.2 us       | 0.21 us     |
| 24 | easybuild     | latency   | diff_node               | OK     | 3.81 us      | 4.0 us      |

---


