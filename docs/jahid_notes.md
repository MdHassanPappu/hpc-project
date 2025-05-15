## SLURM Benchmarking: CPU Binding 
---


## Task 

- check again 4  cases, local. and automate with single scripts.

- reports for local and reframe 

- plot + reframe plot 

- reframe. verify bingyu code( try in my own way ) 

- 
##  1. Allocate a Full Node Exclusively

```bash
salloc -N 1 -n 2 --exclusive
```

- Reserves 1 node entirely for your job.
- Gives access to all cores and memory on the node.

---

## 2. Inspect CPU and NUMA Topology

```bash
lscpu | grep -E "Socket|NUMA|CPU"
```

---

---

### 🔸 Case 1: Intra-node – Same NUMA Node

```bash
srun -n 2 --cpu-bind=mask_cpu:0x1,0x10 osu_get_latency -m 8192:8192

srun -n 2 --cpu-bind=mask_cpu:0x1,0x10 osu_get_bw -m 1048576:1048576
```
- Task 0 on : CPU(s) 0, Socket 0, NUMA node 0

- Task 1 on : CPU(s) 4, Socket 0, NUMA node 0

---

### 🔸 Case 2: Intra-node – Same Socket, Different NUMA Nodes 

```bash
srun -n 2 --cpu-bind=mask_cpu:0x1,0x10000 osu_get_latency -m 8192:8192

srun -n 2 --cpu-bind=mask_cpu:0x1,0x10000 osu_get_bw -m 1048576:1048576
```

- Task 1 on : CPU(s) 16, Socket 0, NUMA node 1
- Task 0 on : CPU(s) 0, Socket 0, NUMA node 0  

---

### 🔸 Case 3: Intra-node – Different Sockets

```bash
srun -n 2 --cpu-bind=mask_cpu:0x1,0x10000000000000000 osu_get_latency -m 8192:8192 

srun -n 2 --cpu-bind=mask_cpu:0x1,0x10000000000000000 osu_get_bw -m 1048576:1048576
```

- Task 0 on : CPU(s) 0, Socket 0, NUMA node 0
- Task 1 on : CPU(s) 64, Socket 1, NUMA node 4

---

### 🔸 Case 4: Inter-node

```bash
salloc -N 2 --exclusive

srun -n 2 -c 1 --cpu-bind=cores osu_get_latency -m 8192:8192

srun -n 2 -c 1 --cpu-bind=cores osu_get_bw -m 1048576:1048576

```

- Each task runs on a different node with 2 cpu cores per task. 


---


------------------------


### Issues i got with reframe test.  

>with reframe it perfertcy binded process for same numa node and different numa node. but not for 
> - diff_numa_same_socket binded to → same numa same socket 
>- diff_socket_same_node  binded to → same socket diff numa node 

- now i'm trying to fix these senario with reframe. 



## Placement Test Summary locally without reframe

| #  | Binary Source | Placement Type         | Latency     | Bandwidth       |
|----|---------------|------------------------|-------------|-----------------|
|  1 | local         | same_numa              | 0.18 us     | 8558.50 MB/s    |
|  2 | local         | diff_numa_same_socket  | 0.18 us     | 9087.26 MB/s    |
|  3 | local         | diff_socket_same_node  | 0.18 us     | 7253.66 MB/s    |
|  4 | local         | diff_node              | 7.00 us     | 2177.70 MB/s    |
|  5 | eessi         | same_numa              | 0.17 us     | 8932.59 MB/s    |
|  6 | eessi         | diff_numa_same_socket  | 0.17 us     | 9848.59 MB/s    |
|  7 | eessi         | diff_socket_same_node  | 0.18 us     | 8213.32 MB/s    |
|  8 | eessi         | diff_node              | 6.96 us     | 2162.74 MB/s    |
|  9 | easybuild     | same_numa              | 0.21 us     | 8549.71 MB/s    |
| 10 | easybuild     | diff_numa_same_socket  | 0.21 us     | 9086.18 MB/s    |
| 11 | easybuild     | diff_socket_same_node  | 0.22 us     | 7123.24 MB/s    |
| 12 | easybuild     | diff_node              | 3.79 us     | 12335.86 MB/s   |


---
## OSU Placement Test Summary for reframe 

After setting reference values for bandwidth and latency, I ran 24 tests across different placement scenarios. Though two placement scenarios are not place correctly `diff_numa_same_socket`, `diff_socket_same_node`.I'm trying to fix them. 

Out of 24 tests:
-  **15 tests passed** 
-  **9 tests failed** 

Below is a detailed breakdown:

Below is a detailed breakdown: Reframe  

| #  | Binary Source | Test Type | Placement Type         | Value        | Target      | Expected | 
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
