import os
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.builtins import parameter
import csv
import datetime
from config import REFERENCE_VALUES, MODULE_CONFIGS


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
            # Local path can be set directly
            osu_dir = os.path.expanduser('~/osu-micro-benchmarks-7.2/build')
            self.executable = os.path.join(
                osu_dir, 'libexec/osu-micro-benchmarks/mpi', 
                self.kind, self.benchmark)
        elif self.binary_source in ['easybuild', 'eessi']:
            # For module-loaded paths, use shell variables instead
            # This will be expanded at runtime after modules are loaded
            self.executable = "${EBROOTOSUMINMICROMINBENCHMARKS}/libexec/osu-micro-benchmarks/mpi/${KIND}/${BENCHMARK}"
            
            # Export variables needed in the shell
            self.prerun_cmds.extend([
                'export KIND="' + self.kind + '"',
                'export BENCHMARK="' + self.benchmark + '"',
                # Add a fallback path finder if the module variable isn't set
                'if [ -z "$EBROOTOSUMINMICROMINBENCHMARKS" ]; then',
                '  echo "Warning: EBROOTOSUMINMICROMINBENCHMARKS not set, trying to find it..."',
                '  OSU_PATH=$(find /opt -name "osu_get_latency" -type f -executable 2>/dev/null | head -1)',
                '  if [ -n "$OSU_PATH" ]; then',
                '    export EBROOTOSUMINMICROMINBENCHMARKS=$(dirname $(dirname $(dirname $(dirname $OSU_PATH))))',
                '    echo "Found at: $EBROOTOSUMINMICROMINBENCHMARKS"',
                '  else',
                '    echo "Could not find OSU Micro-Benchmarks"',
                '    exit 1',
                '  fi',
                'fi',
                'echo "Using OSU benchmarks from: $EBROOTOSUMINMICROMINBENCHMARKS"'
            ])
        else:
            self.skip_if(True, 'Unknown binary source')
            return
        
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
                    ref_key = self.placement_type if self.placement_type  in REFERENCE_VALUES[system][self.metric] else 'default'
                    self.reference = {
                        key: {
                            self.metric: REFERENCE_VALUES[system][self.metric][ref_key]
                        }
                    }
                else:  # bandwidth
                    # For latency, use either multi-node or default reference
                    ref_key = self.placement_type if self.placement_type  in REFERENCE_VALUES[system][self.metric][self.binary_source] else 'default'
                    self.reference = {
                        key: {
                            self.metric: REFERENCE_VALUES[system][self.metric][self.binary_source][ref_key]
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
        
        # Extract performance value safely
        perf_value = "Extraction failed"
        try:
            # Use the perf_variables which should hold the extracted value
            perf_dict = self.perf_variables[self.metric].evaluate(self)
            perf_value = perf_dict['value']
        except Exception as e:
            # Fallback: Try reading from stdout file if performance extraction failed
            try:
                stage_dir = self.stagedir
                stdout_path = os.path.join(stage_dir, self.stdout.evaluate()) # Use evaluated stdout path
                
                if os.path.exists(stdout_path):
                    with open(stdout_path, 'r') as f:
                        content = f.read()
                        import re
                        match = re.search(rf'^\s*{self.test_size}\s+(\S+)', content, re.MULTILINE)
                        if match:
                            perf_value = float(match.group(1))
                        else:
                            match = re.search(rf'\b{self.test_size}\b\s+(\S+)', content, re.MULTILINE)
                            if match:
                                perf_value = float(match.group(1))
                            else:
                                perf_value = "No match found in output"
                else:
                     perf_value = "Output file not found"

            except Exception as fallback_e:
                 perf_value = f"ERROR: Primary: {str(e)}, Fallback: {str(fallback_e)}"

        # Prepare the data row
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Use placement_type if available, otherwise binding_type or N/A
        placement = getattr(self, 'placement_type', getattr(self, 'binding_type', 'N/A'))
        
        data = {
            'timestamp': timestamp,
            'test_name': self.name,
            'system': self.current_system.name,
            'partition': self.current_partition.name,
            'environment': self.current_environ.name,
            'binary_source': self.binary_source,
            'placement_or_binding': placement, # Changed field name
            'benchmark': self.benchmark,
            'metric': self.metric,
            'value': str(perf_value),
            'unit': self.unit,
            'reference': 'N/A'
        }
        
        # Add reference value if available
        try:
            key = f"{self.current_system.name}:{self.current_partition.name}"
            references = self.reference.scope(key)
            if references and self.metric in references:
                ref_value = references[self.metric]
                # Handle tuple format (value, low_thres, high_thres, unit)
                if isinstance(ref_value, tuple):
                    data['reference'] = ref_value[0] 
                else:
                    data['reference'] = ref_value
        except Exception:
            pass # Keep reference as N/A if lookup fails
        
        # Write to CSV file
        try:
            with open(csv_file, 'a', newline='') as f:
                # Ensure all keys are present in the header, even if N/A
                fieldnames = [
                    'timestamp', 'test_name', 'system', 'partition', 
                    'environment', 'binary_source', 'placement_or_binding', 
                    'benchmark', 'metric', 'value', 'unit', 'reference'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists or os.path.getsize(csv_file) == 0:
                    writer.writeheader()
                # Ensure all fields are present in the row, defaulting to N/A if missing
                row_to_write = {field: data.get(field, 'N/A') for field in fieldnames}
                writer.writerow(row_to_write)
        except Exception as e:
            print(f"ERROR writing to CSV: {str(e)}")


@rfm.simple_test
class OSUDistributionPlacementTest(OSUMicroBenchmarkBase):
    """Tests process placement using Slurm's --distribution mechanism"""
    
    placement_type = parameter([
        'same_numa',
        'diff_numa_same_socket', 
        'diff_socket_same_node', 
        'diff_node'
    ])

    @run_after('setup')
    def set_placement_references(self):
        """Set reference values based on placement type"""
        is_multi = (self.placement_type == 'diff_node')
        self.set_reference_values(is_multi_node=is_multi)
        self.tags.add(f"dist_{self.placement_type}")

    @run_before('run')
    def set_job_options_for_placement(self):
        """Configure Slurm distribution options for different placement strategies"""
        self.num_tasks = 2
        self.num_cpus_per_task = 1
        self.exclusive = False  # Allow resource sharing
        self.job.launcher.options = []  # Reset options
        
        script_path = os.path.expanduser('~/hpc-project/scripts/2.Hardware-Detection.sh')
        self.prerun_cmds.append(f'chmod +x {script_path}')
    
        # Add it to postrun commands for verification
        self.postrun_cmds = [f'srun -n2 {script_path}']
    
        if self.placement_type == 'same_numa':
            self.num_nodes = 1
            self.num_tasks_per_node = 2
            
            # Pack tasks onto the same core group to ensure same NUMA node
            self.job.launcher.options = [
                '--distribution=block:block:block',  # Simple block distribution
                '--cpu-bind=none'        # No specific binding
            ]
            
            # Add verification directly in launcher
            self.prerun_cmds.append('echo "Verifying same NUMA placement:"')
            self.postrun_cmds = ['srun -n2 ./verify_placement.sh']

        elif self.placement_type == 'diff_numa_same_socket':
            self.num_nodes = 1
            self.num_tasks_per_node = 2
            
            # First check if we have multiple NUMA per socket
            self.prerun_cmds.extend([
                'NUMA_PER_SOCKET=$(( $NUMA_COUNT / $SOCKET_COUNT ))',
                'echo "- $NUMA_PER_SOCKET NUMA node(s) per socket"'
            ])
            
            # Try to distribute across NUMA domains
            self.job.launcher.options = [
                '--distribution=block:cyclic:block',  # Cyclic distribution
                '--cpu-bind=cores'        # Bind to cores
            ]
            
            # Add verification
            self.prerun_cmds.append('echo "Verifying different NUMA placement:"')
            self.postrun_cmds = ['srun -n2 ./verify_placement.sh']

        elif self.placement_type == 'diff_socket_same_node':
            self.num_nodes = 1
            self.num_tasks_per_node = 2
            
            # Check if we have multiple sockets
            self.prerun_cmds.extend([
                'if [ "$SOCKET_COUNT" -lt 2 ]; then',
                '  echo "WARNING: System has only $SOCKET_COUNT socket(s). This test requires at least 2."',
                'fi'
            ])
            
            # Try to distribute across sockets if possible
            self.job.launcher.options = [
                '--distribution=block:cyclic',   # Try to spread across sockets
                '--cpu-bind=sockets'             # Bind to sockets
            ]
            
            # Add verification
            self.prerun_cmds.append('echo "Verifying different socket placement:"')
            self.postrun_cmds = ['srun -n2 ./verify_placement.sh']

        elif self.placement_type == 'diff_node':
            # Make it flexible based on allocation
            self.num_nodes = 2  
            self.num_tasks_per_node = 1  
            
            # Use the shell variable in launcher options
            # distributes tasks across nodes in a round-robin fashion
            self.job.launcher.options = ['-N2 -n2 --ntasks-per-node=1 --exclusive --distribution=cyclic:block:block']
            
            # Add verification
            self.prerun_cmds.append('echo "Verifying node distribution:"')
            self.postrun_cmds = ['srun -n2 ./verify_placement.sh']