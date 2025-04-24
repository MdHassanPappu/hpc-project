import os
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.builtins import parameter
import csv
import datetime
from config import REFERENCE_VALUES, BINDING_CONFIGS, MODULE_CONFIGS


class OSUMicroBenchmarkBase(rfm.RunOnlyRegressionTest):
    """Base class for OSU Micro-Benchmark tests"""
    
    valid_systems = ['*']
    valid_prog_environs = ['*']
    
    num_warmup_iters = 10
    num_iters = 1000
    device_buffers = 'cpu'
    kind = 'one-sided'
    test_type = parameter([
        ('osu_get_latency', 'latency'),
        ('osu_get_bw', 'bandwidth')
    ])
    
    # Define message sizes
    latency_size = 8192     # 8K bytes
    bandwidth_size = 1048576  # 1MB
    
    time_limit = '10m'
    exclusive = True
    
    # Add parameter for binary source
    binary_source = parameter(['local', 'easybuild', 'eessi'])
    
    @run_before('setup')
    def setup_per_benchmark(self):
        """Setup benchmark-specific parameters"""
        self.benchmark, self.metric = self.test_type
        
        # Determine unit based on metric
        if self.metric == 'latency':
            self.test_size = self.latency_size
            self.unit = 'us'
        else:  # bandwidth
            self.test_size = self.bandwidth_size
            self.unit = 'MB/s'
            
        # Set up the performance variable with our custom function
        self.perf_variables = {
            self.metric: sn.make_performance_function(
                self._extract_metric(self.test_size), self.unit
            )
        } 
        
    @run_before('run')
    def load_modules(self):
        """Load necessary modules based on binary source"""
        self.modules = []  
        
        self.prerun_cmds.extend(MODULE_CONFIGS[self.binary_source])
                
    @run_before('run')    
    def set_executable(self):
        """Set executable path and options"""
        if self.binary_source == 'local':
            osu_dir = os.path.expanduser('~/osu-micro-benchmarks-7.2/build')
        elif self.binary_source in ['easybuild', 'eessi']:
            osu_dir = os.environ.get('EBROOTOSUMINMICROMINBENCHMARKS')
            
        if not osu_dir:
            self.skip_if(True, 'OSU Micro-Benchmarks not installed')
            return
            
        self.executable = os.path.join(
            osu_dir, 'libexec/osu-micro-benchmarks/mpi', 
            self.kind, self.benchmark)
        
        # Set basic executable options
        self.executable_opts = [
            '-m', str(self.test_size),
            '-x', str(self.num_warmup_iters),
            '-i', str(self.num_iters)
        ]
        
        # Verify executable exists
        self.prerun_cmds.append(
            f'if [ ! -x "{self.executable}" ]; then '
            f'echo "Benchmark executable not found: {self.executable}"; exit 1; fi'
        )
    
    def _extract_metric(self, size):
        """Extract benchmark metric from stdout with specific size"""
        return sn.extractsingle(rf'^{size}\s+(\S+)',
                               self.stdout, 1, float)
    
    @sanity_function
    def assert_output(self):
        return sn.assert_found(r'# OSU MPI', self.stdout)
    
    def set_reference_values(self, is_multi_node=False):
        """Common method to set reference values based on configuration"""
        system = self.current_system.name
        partition = self.current_partition.name  

        # Create reference key with environment
        key = f"{system}:{partition}"
        self.reference = dict()
        
        if system in REFERENCE_VALUES:
            # Set metric-specific reference values
            if self.metric in REFERENCE_VALUES[system]:
                if self.metric == 'latency':
                    # For latency, use either multi-node or default reference
                    ref_key = 'multi_node' if is_multi_node else 'default'
                    self.reference = {
                        key: {
                            self.metric: REFERENCE_VALUES[system][self.metric][ref_key]
                        }
                    }
                else:  # bandwidth
                    if hasattr(self, 'binding_type'):
                        # For binding tests, use binding-specific references
                        if self.binary_source in REFERENCE_VALUES[system][self.metric]:
                            if self.binding_type in REFERENCE_VALUES[system][self.metric][self.binary_source]:
                                self.reference = {
                                    key: {
                                        self.metric: REFERENCE_VALUES[system][self.metric][self.binary_source][self.binding_type]
                                    }
                                }
                    elif is_multi_node:
                        # For multi-node tests without binding
                        self.reference = {
                            key: {
                                self.metric: REFERENCE_VALUES[system][self.metric][self.binary_source]['multi_node']
                            }
                        }
                    else:
                        # For default bandwidth tests
                        self.reference = {
                            key: {
                                self.metric: REFERENCE_VALUES[system][self.metric][self.binary_source]['default']
                            }
                        }
        # print(f"Reference {self.reference}")                
        
    
    @run_after('performance')
    def log_to_csv(self):
        """Append performance results to a CSV file"""
        # Make sure directory exists
        csv_dir = os.path.expanduser('~/hpc-project/log')
        os.makedirs(csv_dir, exist_ok=True)
        csv_file = os.path.join(csv_dir, 'osu_perf_results.csv')
        file_exists = os.path.isfile(csv_file)
        
        # Extract performance value safely - use the job's stdout path directly
        try:
            # Get the actual path of the job's stdout file
            stage_dir = self.stagedir
            # Try multiple potential output file paths
            potential_paths = [
                os.path.join(stage_dir, 'rfm_job.out'),
                os.path.join(stage_dir, f'{self.job.jobid}.out'),
                os.path.join(stage_dir, 'job.out'),
                os.path.join(stage_dir, 'stdout'),
                str(self.stdout)  # Keep original as fallback
            ]
            
            stdout_path = None
            for path in potential_paths:
                if os.path.exists(path):
                    stdout_path = path
                    print(f"Found output file at: {stdout_path}")
                    break                
            # print(f"stdout_path: {stdout_path}")
            if os.path.exists(stdout_path):
                with open(stdout_path, 'r') as f:
                    content = f.read()
                    import re
                    # print(f"Content: {content}")
                    # print(f'^\s*{self.test_size}\s+(\S+)')
                    match = re.search(rf'^\s*{self.test_size}\s+(\S+)', content, re.MULTILINE)
                    if match:
                        perf_value = float(match.group(1))
                    else:
                        # Fallback to a more flexible pattern in case formatting varies
                        match = re.search(rf'\b{self.test_size}\b\s+(\S+)', content, re.MULTILINE)
                        if match:
                            perf_value = float(match.group(1))
                        else:
                            perf_value = "No match found in output"
            else:
                # If stdout file doesn't exist, get it from performance if available
                perf_dict = getattr(self, 'perf_info', {})
                if self.metric in perf_dict:
                    perf_value = perf_dict[self.metric]['value']
                else:
                    perf_value = "Output file not available"
        except Exception as e:
            perf_value = f"ERROR: {str(e)}"
        
        # Prepare the data row
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        binding = getattr(self, 'binding_type', 'N/A')
        data = {
            'timestamp': timestamp,
            'test_name': self.name,
            'system': self.current_system.name,
            'partition': self.current_partition.name,
            'environment': self.current_environ.name,
            'binary_source': self.binary_source,
            'binding_type': binding,
            'benchmark': self.benchmark,
            'metric': self.metric,
            'value': str(perf_value),  # Convert to string to handle various types
            'unit': self.unit,
            'reference': 'N/A'
        }
        
        # Add reference value if available
        try:
            # Fix the reference key format to match what's in set_reference_values
            key = f"{self.current_system.name}:{self.current_partition.name}"
            references = self.reference.scope(key)
            if references and self.metric in references:
                ref_value = references[self.metric]
                data['reference'] = ref_value
        except Exception:
            pass
        
        # Write to CSV file with proper error handling
        try:
            with open(csv_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(data)
        except Exception as e:
            print(f"ERROR writing to CSV: {str(e)}")


@rfm.simple_test
class OSUGetBindingTest(OSUMicroBenchmarkBase):
    """Tests T1-T7: Various binding strategies on single node"""
    binding_type = parameter(list(BINDING_CONFIGS.keys()))
    
    @run_after('setup')
    def set_binding_specific_references(self):
        """Set appropriate reference values based on binding type"""
        self.set_reference_values(is_multi_node=False)
    
    @run_before('run')
    def set_job_options(self):
        """Configure binding options"""
        self.num_tasks = 2
        self.num_nodes = 1
        self.num_cpus_per_task = 1
        self.num_tasks_per_node = 2
        
        # Special setup for CPU mapping binding strategies
        if self.binding_type == 'map_cpu':
            self.prerun_cmds.append('CORES=$(taskset -cp $$ | grep -o "[0-9,]*$" | tr "," "\\n" | sort -n)')
            self.prerun_cmds.append('MIN_ID=$(echo "$CORES" | head -n1)')
            self.prerun_cmds.append('MAX_ID=$(echo "$CORES" | tail -n1)')
        elif self.binding_type == 'map_cpu_nb':
            self.prerun_cmds.append('CORES=$(taskset -cp $$ | grep -o "[0-9,]*$" | tr "," "\\n" | sort -n)')
            self.prerun_cmds.append('MID1=$(echo "$CORES" | head -n2 | tail -n1)')
            self.prerun_cmds.append('MID2=$(echo "$CORES" | head -n3 | tail -n1)')
        
        # Set job launcher options based on binding type
        self.job.launcher.options = [BINDING_CONFIGS[self.binding_type]['option']]


@rfm.simple_test
class OSUGetNumaAwareTest(OSUMicroBenchmarkBase):
    """Test T8: NUMA-aware placement"""
    
    @run_after('setup')
    def set_numa_reference_values(self):
        """Set reference values for NUMA-aware test"""
        self.set_reference_values(is_multi_node=False)
             
    @run_before('run')
    def set_job_options(self):
        """Configure NUMA-aware options"""
        self.num_tasks = 2
        self.num_nodes = 1        
        self.num_cpus_per_task = 1
        self.num_tasks_per_node = 2
        
        # Determine NUMA node for the first available CPU
        self.prerun_cmds.extend([
            'MIN_ID=$(taskset -cp $$ | grep -o "[0-9,]*$" | tr "," "\\n" | sort -n | head -n1)',
            'NUMA_NODE=$(numactl --hardware | awk -v cid=${MIN_ID} \'/node [0-9]+ cpus:/{for(i=4;i<=NF;i++) if($i==cid){match($0,/node ([0-9]+)/,m); print m[1]; exit}}\')',
            'if [ -z "$NUMA_NODE" ]; then NUMA_NODE=0; fi',
            'export NUMA_NODE',
        ])
        
        self.job.launcher.options = []
        
        # Use numactl for NUMA-aware placement
        original_exe = self.executable              
        self.executable = 'numactl'
        self.executable_opts = [
            '--cpunodebind=$NUMA_NODE',
            '--membind=$NUMA_NODE',
            original_exe
        ] + self.executable_opts


@rfm.simple_test
class OSUGetMultiNodeTest(OSUMicroBenchmarkBase):
    """Tests T9-T13: Multi-node communication tests"""
    binding_type = parameter(list(BINDING_CONFIGS.keys()))
    
    @run_after('setup')
    def set_binding_specific_references(self):
        """Set appropriate reference values based on binding type"""
        self.set_reference_values(is_multi_node=True)
    
    @run_before('run')
    def set_job_options(self):
        """Configure multi-node options"""
        self.num_tasks = 2
        self.num_nodes = 2
        self.num_cpus_per_task = 1
        self.num_tasks_per_node = 1
        
        # Skip multi-node tests if we don't have enough nodes
        self.prerun_cmds.append(
            'NODE_COUNT=$(scontrol show hostnames | wc -l); '
            'if [ "$NODE_COUNT" -lt 2 ]; then '
            'echo "ERROR: Need at least 2 nodes for multi-node tests"; '
            'echo "Current allocation has $NODE_COUNT node(s)"; '
            'exit 1; fi'
        )
        
        # Set job launcher options based on binding type
        if self.binding_type != 'none':
            self.job.launcher.options = [BINDING_CONFIGS[self.binding_type]['option']]