import os
import reframe as rfm
import reframe.utility.sanity as sn
from .4.1-OSU0BENCHMARK-BASE import OSUMicroBenchmarkBase
# Add these classes after the existing OSUGetMultiNodeTest class

@rfm.simple_test
class OSUPt2PtLatencyTest(OSUMicroBenchmarkBase):
    """Point-to-point latency test"""
    descr = 'OSU Point-to-point Latency test'
    kind = 'pt2pt/standard'
    benchmark = 'osu_latency'
    metric = 'latency'
    num_tasks = 2
    num_tasks_per_node = 1
    
    @run_after('setup')
    def set_reference_values(self):
        """Set reference values based on the benchmark being run"""
        key = f'{self.current_system.name}:{self.current_partition.name}'
        self.reference = {key: {}}

        if key == 'aion:batch':
            self.reference[key][self.metric] = (0.19, -0.05, 0.05, 'us')
        elif key == 'iris:batch':
            self.reference[key][self.metric] = (0.21, -0.05, 0.05, 'us')


@rfm.simple_test
class OSUPt2PtBandwidthTest(OSUMicroBenchmarkBase):
    """Point-to-point bandwidth test"""
    descr = 'OSU Point-to-point Bandwidth test'
    kind = 'pt2pt/standard'
    benchmark = 'osu_bw'
    metric = 'bandwidth'
    num_tasks = 2
    num_tasks_per_node = 1
    
    @run_after('setup')
    def set_reference_values(self):
        """Set reference values based on the benchmark being run"""
        key = f'{self.current_system.name}:{self.current_partition.name}'
        self.reference = {key: {}}

        if key == 'aion:batch':
            self.reference[key][self.metric] = (9500, -0.05, 0.05, 'MB/s')
        elif key == 'iris:batch':
            self.reference[key][self.metric] = (5000, -0.05, 0.05, 'MB/s')


@rfm.simple_test
class OSUCollectiveAllreduceTest(OSUMicroBenchmarkBase):
    """Collective allreduce test"""
    descr = 'OSU Collective Allreduce test'
    kind = 'collective/blocking'
    benchmark = 'osu_allreduce'
    metric = 'latency'
    num_tasks = parameter([4, 8, 16])  # Test with different process counts
    num_tasks_per_node = 4
    
    @run_after('setup')
    def set_reference_values(self):
        """Set reference values based on the benchmark being run"""
        key = f'{self.current_system.name}:{self.current_partition.name}'
        self.reference = {key: {}}

        # References vary by process count
        if key == 'aion:batch':
            if self.num_tasks == 4:
                self.reference[key][self.metric] = (1.1, -0.1, 0.1, 'us')
            elif self.num_tasks == 8:
                self.reference[key][self.metric] = (1.8, -0.1, 0.1, 'us')
            else:  # 16
                self.reference[key][self.metric] = (2.5, -0.1, 0.1, 'us')


@rfm.simple_test
class OSUCollectiveAlltoallTest(OSUMicroBenchmarkBase):
    """Collective alltoall test"""
    descr = 'OSU Collective Alltoall test'
    kind = 'collective/blocking'
    benchmark = 'osu_alltoall'
    metric = 'latency'
    num_tasks = parameter([4, 8, 16])  # Test with different process counts
    num_tasks_per_node = 4
    
    @run_after('setup')
    def set_reference_values(self):
        """Set reference values based on the benchmark being run"""
        key = f'{self.current_system.name}:{self.current_partition.name}'
        self.reference = {key: {}}

        # References vary by process count
        if key == 'aion:batch':
            if self.num_tasks == 4:
                self.reference[key][self.metric] = (2.5, -0.1, 0.1, 'us')
            elif self.num_tasks == 8:
                self.reference[key][self.metric] = (5.0, -0.1, 0.1, 'us')
            else:  # 16
                self.reference[key][self.metric] = (9.0, -0.1, 0.1, 'us')


@rfm.simple_test
class OSUBindingTestPt2Pt(OSUMicroBenchmarkBase):
    """Test binding strategies with point-to-point communication"""
    
    kind = 'pt2pt/standard'
    benchmark = 'osu_latency'
    metric = 'latency'
    
    binding_type = parameter([
        'threads',     # Same core, SMT siblings  
        'cores',       # Same socket, different cores
        'sockets',     # Different sockets
        'none'         # No binding
    ])
    
    @run_before('run')
    def set_job_options(self):
        self.num_tasks = 2
        self.num_nodes = 1
        self.num_cpus_per_task = 1
        self.num_tasks_per_node = 2
        
        if self.binding_type == 'threads':
            self.job.launcher.options = ['--cpu-bind=threads']
        elif self.binding_type == 'cores':
            self.job.launcher.options = ['--cpu-bind=cores']
        elif self.binding_type == 'sockets':
            self.job.launcher.options = ['--cpu-bind=sockets']
        elif self.binding_type == 'none':
            self.job.launcher.options = ['--cpu-bind=None']


@rfm.simple_test
class OSUMultiNodeTest(OSUMicroBenchmarkBase):
    """Multi-node tests with different communication patterns"""
    
    # Test multiple benchmark types across nodes
    benchmark_kind = parameter([
        ('pt2pt/standard', 'osu_latency', 'latency'),
        ('pt2pt/standard', 'osu_bw', 'bandwidth'),
        ('collective/blocking', 'osu_allreduce', 'latency'),
        ('collective/blocking', 'osu_alltoall', 'latency')
    ])
    
    @run_after('init')
    def set_test_attributes(self):
        self.kind, self.benchmark, self.metric = self.benchmark_kind
        
        # For collective tests, use more processes
        if self.kind.startswith('collective'):
            self.num_tasks = 8
            self.num_tasks_per_node = 4
            self.num_nodes = 2
        else:
            self.num_tasks = 2
            self.num_tasks_per_node = 1
            self.num_nodes = 2
    
    @run_before('run')
    def set_job_options(self):
        # Skip multi-node tests if we don't have enough nodes
        self.prerun_cmds.append(
            'NODE_COUNT=$(scontrol show hostnames | wc -l); '
            'if [ "$NODE_COUNT" -lt 2 ]; then '
            'echo "ERROR: Need at least 2 nodes for multi-node tests"; '
            'echo "Current allocation has $NODE_COUNT node(s)"; '
            'exit 1; fi'
        )
        
        # Basic binding to distribute tasks evenly
        self.job.launcher.options = ['--cpu-bind=cores']