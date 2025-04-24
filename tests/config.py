# Configuration dictionaries - move these to the top for easy modification
BINDING_CONFIGS = {
    'threads': {'option': '--cpu-bind=threads', 'desc': 'Same core, SMT siblings'},
    'cores': {'option': '--cpu-bind=cores', 'desc': 'Same socket, different cores'},
    'sockets': {'option': '--cpu-bind=sockets', 'desc': 'Different sockets'},
    'ldoms': {'option': '--cpu-bind=ldoms', 'desc': 'Different NUMA domains'},
    'map_cpu': {'option': '--cpu-bind=map_cpu:${MIN_ID},${MAX_ID}', 'desc': 'Max hop / farthest cores'},
    'map_cpu_nb': {'option': '--cpu-bind=map_cpu:${MID1},${MID2}', 'desc': 'Neighboring sockets'},
    'none': {'option': '--cpu-bind=None', 'desc': 'No binding'}
}

# Reference values by system, binding type, and binary source
REFERENCE_VALUES = {
    'aion': {
        'latency': {
            'default': (0.21, -0.05, 0.05, 'us'),
            'multi_node': (3.9, -0.2, 0.2, 'us')
        },
        'bandwidth': {
            'eessi': {
                'default': (8300, -0.2, 0.2, 'MB/s'),
                'threads': (4000, -0.2, 0.2, 'MB/s'),
                'cores': (2000, -0.2, 0.2, 'MB/s'),
                'sockets': (2000, -0.2, 0.2, 'MB/s'),
                'ldoms': (2000, -0.2, 0.2, 'MB/s'),
                'map_cpu': (2000, -0.2, 0.2, 'MB/s'),
                'map_cpu_nb': (4000, -0.2, 0.2, 'MB/s'),
                'none': (8200, -0.2, 0.2, 'MB/s'),
                'multi_node': (8300, -0.2, 0.2, 'MB/s')
            },
            'easybuild': {                
                'default': (8300, -0.2, 0.2, 'MB/s'),
                'threads': (6000, -0.2, 0.2, 'MB/s'),
                'cores': (5700, -0.2, 0.2, 'MB/s'),
                'sockets': (4000, -0.2, 0.2, 'MB/s'),
                'ldoms': (7000, -0.2, 0.2, 'MB/s'),
                'map_cpu': (3300, -0.2, 0.2, 'MB/s'),
                'map_cpu_nb': (3000, -0.2, 0.2, 'MB/s'),
                'none': (3200, -0.2, 0.2, 'MB/s'),
                'multi_node': (8300, -0.2, 0.2, 'MB/s')
            },
            'local': {                
                'default': (8300, -0.2, 0.2, 'MB/s'),
                'threads': (8400, -0.2, 0.2, 'MB/s'),
                'cores': (3600, -0.2, 0.2, 'MB/s'),
                'sockets': (3200, -0.2, 0.2, 'MB/s'),
                'ldoms': (3500, -0.2, 0.2, 'MB/s'),
                'map_cpu': (3000, -0.2, 0.2, 'MB/s'),
                'map_cpu_nb': (4100, -0.2, 0.2, 'MB/s'),
                'none': (2300, -0.2, 0.2, 'MB/s'),
                'multi_node': (8300, -0.2, 0.2, 'MB/s')
            },
        }
    },
    'iris': {
        'latency': {
            'default': (0.21, -0.2, 0.2, 'us'),
            'multi_node': (3.9, -0.2, 0.2, 'us')
        },
        'bandwidth': {
            'eessi': {                
                'default': (8300, -0.2, 0.2, 'MB/s'),
                'threads': (3200, -0.2, 0.2, 'MB/s'),
                'cores': (2400, -0.2, 0.2, 'MB/s'),
                'sockets': (1800, -0.2, 0.2, 'MB/s'),
                'ldoms': (6200, -0.2, 0.2, 'MB/s'),
                'map_cpu': (5700, -0.2, 0.2, 'MB/s'),
                'map_cpu_nb': (4150, -0.2, 0.2, 'MB/s'),
                'none': (8300, -0.2, 0.2, 'MB/s'),
                'multi_node': (8300, -0.2, 0.2, 'MB/s')
            },
            'easybuild': {                
                'default': (8300, -0.2, 0.2, 'MB/s'),
                'threads': (8100, -0.2, 0.2, 'MB/s'),
                'cores': (8400, -0.2, 0.2, 'MB/s'),
                'sockets': (4300, -0.2, 0.2, 'MB/s'),
                'ldoms': (6200, -0.2, 0.2, 'MB/s'),
                'map_cpu': (5700, -0.2, 0.2, 'MB/s'),
                'map_cpu_nb': (4100, -0.2, 0.2, 'MB/s'),
                'none': (3200, -0.2, 0.2, 'MB/s'),
                'multi_node': (8300, -0.2, 0.2, 'MB/s')
            },
            'local': {
                'threads': (2700, -0.2, 0.2, 'MB/s'),
                'cores': (3000, -0.2, 0.2, 'MB/s'),
                'sockets': (2200, -0.2, 0.2, 'MB/s'),
                'ldoms': (5000, -0.2, 0.2, 'MB/s'),
                'map_cpu': (4700, -0.2, 0.2, 'MB/s'),
                'map_cpu_nb': (4100, -0.2, 0.2, 'MB/s'),
                'none': (2200, -0.2, 0.2, 'MB/s'),
                'multi_node': (8300, -0.2, 0.2, 'MB/s')
            },
        }
    }
}

MODULE_CONFIGS = {
            'local': [
                'module load env/testing/2023b || echo "Warning: Could not load env module"',
                'module load toolchain/foss/2023b || echo "Warning: Could not load foss toolchain"'
            ],
            'easybuild': [
                'module load tools/EasyBuild/5.0.0 || echo "Warning: Could not load EasyBuild"',
                'module load perf/OSU-Micro-Benchmarks/7.2-gompi-2023b || echo "Warning: Could not load OSU benchmarks"'
            ],
            'eessi': [
                'module load EESSI || echo "Warning: Could not load EESSI"',
                'module load OSU-Micro-Benchmarks/7.2-gompi-2023b || echo "Warning: Could not load OSU benchmarks"'
            ]
        }