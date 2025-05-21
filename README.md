# 🔍 **MPI Performance Testing Suite**

A comprehensive **performance testing framework** using **ReFrame** to measure and monitor MPI communication performance on the **ULHPC clusters** (IRIS and Aion).

## Project Goal

This project builds a testing suite to measure MPI communication latency and bandwidth, helping to detect unexpected performance drops over time due to system updates, hardware changes, or other factors.

## 🔧 **Technologies**

- **ReFrame**: Framework for automated testing and result tracking
- **OSU Micro-Benchmarks (OMB)**: Industry-standard MPI benchmarking tools
	- `osu_latency`: Measures communication delay
	- `osu_bw`: Measures communication throughput

## 📋 **Requirements**

- **Target Clusters**: 
	- IRIS (CPU nodes only)
	- Aion

- **Benchmark Parameters**:
	- `osu_latency`: 8192 bytes message size
	- `osu_bw`: 1MB (1,048,576 bytes) message size

- **Testing Environments**:
	- Local build
	- EasyBuild
	- EESSI

## 🧪 **Test Scenarios**

This suite measures MPI performance across four key communication scenarios:

1. **Same NUMA node**: Both processes on the same NUMA node
2. **Different NUMA node**: Processes on the same physical socket but different NUMA nodes
3. **Different Sockets**: Processes on the same compute node but different sockets
4. **Different nodes**: Processes running on separate compute nodes

## 📦 **Installation**

Install OSU Micro-Benchmarks using one of these methods:

```bash
cd scripts

# Local installation
./1.Install-OSU-Micro-Benchmarks --method local
# Source the generated environment file
source /tmp/osu_env_*.sh

# EESSI installation
./1.Install-OSU-Micro-Benchmarks --method eessi

# EasyBuild installation
./1.Install-OSU-Micro-Benchmarks --method easybuild
```

## 🚀 **Usage**

### Hardware Detection

Analyze and detect the cluster hardware topology:
```bash
cd scripts
./2.Hardware-Detection
```

### Running Tests with ReFrame

Execute the complete test suite:
```bash
cd tests/
./run.sh
```

This will automatically run all benchmark tests and generate performance reports.

## 📊 **Results**

Test results are stored in the ReFrame output directory and can be used to track performance trends over time.