# 🔍 **Project Goal**

You're building a **performance testing suite** using **ReFrame** to **measure MPI communication** latency and bandwidth on the **ULHPC clusters (IRIS and Aion)**.

You'll use:

- **OSU Micro-Benchmarks (OMB)** — specifically:
	- `osu_latency`: to measure **latency** (communication delay)	
	- `osu_bw`: to measure **bandwidth** (communication speed)

The big idea: You want to catch any **unexpected performance drops** in the cluster over time (due to updates, hardware changes, etc.) using **regression tests**.

---

# Schedule

`Aion` - Jahid  
`Iris` - JIANG  

week 1: 
1. Install three ways; 
2. **Intra-socket** —  Jahid  
	**Inter-socket** — Jiang
3. simple report: graph
4. create github
5. write down everything
6. optional: write scripts steps by steps.

Next discussion: **21th April, Monday, 14:00**

week 2: **Inter-node** 

week 3: Advanced optimazation

---

# 📦 **What You'll Use**

- **Clusters**: IRIS (CPU nodes only) and Aion
- **Benchmark tool**: OSU Micro-Benchmarks v7.2

- **Message sizes**:
	- `osu_latency`: 8192 bytes	
	- `osu_bw`: 1MB (1,048,576 bytes)

- **Toolchains and environments**:
	- `env/testing/2023b`
	- `foss/2023b` toolchain (for local compilation)
	```bash
	module purge
	module load env/development/2023b
	module load toolchain/foss/2023b
	```
- **ReFrame**: to automate tests and track results over time
```bash
module use /opt/apps/easybuild/systems/aion/rhel810-20250216/2023b/epyc/modules/all
module load devel/ReFrame/4.7.3-GCCcore-13.2.0
```

---

# 🧪 **Test Design**

You'll test how MPI performs in different hardware configurations:

## 👇 Focus on 3 Communication Scenarios

1. **Intra-socket** — same socket (same NUMA node)
2. **Inter-socket** — different sockets on the same node
3. **Inter-node** — across two physical compute nodes

Use the `hwloc` tool to find where processes are running (NUMA topology).

---

# 🛠️ **Three Ways to Use OSU Benchmarks**

You must test performance using all three versions of the benchmarks:

1. **Locally Compiled**
	- Compile from source **inside ReFrame**
	- Use `foss/2023b` toolchain
```bash
cd ~/project
export OSU_VERSION=7.2 # Just to abstract from the version to download 
wget https://mvapich.cse.ohio-state.edu/download/mvapich/osu-micro-benchmarks-${OSU_VERSION}.tar.gz
tar -zxvf osu-micro-benchmarks-${OSU_VERSION}.tar.gz 
cd osu-micro-benchmarks-${OSU_VERSION}

mkdir build # Prepare the specific building directory 
cd build 
echo $OSU_VERSION # Check that the variable is defined and with teh appropriate value # Load the appropriate module 
module load toolchain/foss/2023b # Configure the Foss MPI-based build for installation in the current directory 
../configure CC=mpicc CFLAGS=-I$(pwd)/../util --prefix=$(pwd) 
make && make install
```
2. **EasyBuild Compiled**
	- Load a pre-built EasyBuild module	
	```bash
	module purge
	module load tools/EasyBuild/5.0.0
	eb ~/.local/easybuild/software/EasyBuild/5.0.0/easybuild/easyconfigs/o/OSU-Micro-Benchmarks/OSU-Micro-Benchmarks-7.2-gompi-2023b.eb
	module load perf/OSU-Micro-Benchmarks/7.5-gompi-2023b
	```
	Use `module show perf/OSU-Micro-Benchmarks/7.5-gompi-2020b` to locate the path `~/.local/easybuild/software/OSU-Micro-Benchmarks/7.5-gompi-2020b/easybuild/`. Then copy `log` file and `eb` file to `omb`.
3. **Precompiled from EESSI**
	- Use the EESSI software stack
	```bash
	module load EESSI
	modile load OSU-Micro-Benchmarks/7.2-gompi-2023b
	```

Each test case should work with **each of these three binary sources**.

## Verification

```bash
cd libexec/osu-micro-benchmarks/mpi/one-sided/ 
srun -n 2 ./osu_get_latency 
srun -n 2 ./osu_get_bw
```

---

# 📊 **Expected Performance (Baseline Values)**

Use these as **reference values** in your regression tests:

| Test | Cluster | Config | Expected Value |
|-------------|---------|---------------|---------------------|
| osu_latency | Aion | Intra-node | ~2.3 µs |
| osu_latency | Aion | Inter-node | ~3.9 µs |
| osu_bw | Aion | Any config | ~12,000 MB/s |

Your ReFrame tests should **fail** if performance drops significantly from these, **unless** such a drop is expected (e.g., system update).

---

# 📂 **What You Need to Deliver**

## 1. ✅ ReFrame Test Scripts

- For each binary source (local, EasyBuild, EESSI)
- For each scenario (intra-socket, inter-socket, inter-node)
- For each cluster (IRIS and Aion)
- Fully documented

## 2. 📈 Performance Report

- Graphs showing results for each scenario + binary source
- Analysis explaining:
- Why you chose specific test cases
- Why your reference values are valid
- What changes might affect those values

## 3. 📁 Git Repository

- All scripts, configs, and documentation
- Instructions to clone and run the tests

## 4. 🎤 Final Evaluation

- 10-minute presentation: goals, methods, findings
- 15–20 minute live demo:
- Start from scratch (clone repo)
- Load modules
- Run tests in ReFrame
- Show that results match your report

---

# 🧠 Strategy Tips

- Start testing **intra-node** cases first (easier to debug).

- Use `hwloc` to **pin processes** to specific sockets/cores.

- Use ReFrame's **performance reference system** to define pass/fail thresholds.

- Keep your test scripts **modular** so you can reuse logic across scenarios and clusters.
