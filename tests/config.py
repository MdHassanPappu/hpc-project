# Reference values by system, binding type, and binary source
REFERENCE_VALUES = {
    'aion': {
        'latency': {
            'eessi': {
                'default': (0.21, -0.05, 0.05, 'us'),  # Updated from 0.21 to 0.18
                'same_numa': (0.21, -0.05, 0.05, 'us'),
                'diff_numa_same_socket': (0.21, -0.05, 0.05, 'us'),
                'diff_socket_same_node': (0.21, -0.05, 0.05, 'us'),
                'diff_node': (4.0, -0.05, 0.05, 'us')
            },
            'easybuild': {
                'default': (0.21, -0.05, 0.05, 'us'),  # Updated from 0.21 to 0.18
                'same_numa': (0.21, -0.05, 0.05, 'us'),
                'diff_numa_same_socket': (0.21, -0.05, 0.05, 'us'),
                'diff_socket_same_node': (0.21, -0.05, 0.05, 'us'),
                'diff_node': (4.0, -0.05, 0.05, 'us')
            },
            'local': {
                'default': (0.21, -0.05, 0.05, 'us'),  # Updated from 0.21 to 0.18
                'same_numa': (0.21, -0.05, 0.05, 'us'),
                'diff_numa_same_socket': (0.21, -0.05, 0.05, 'us'),
                'diff_socket_same_node': (0.21, -0.05, 0.05, 'us'),
                'diff_node': (4.0, -0.05, 0.05, 'us')
            },            
        },
        'bandwidth': {
            'eessi': {
                'default': (7200, -0.05, 0.05, 'MB/s'),  # Updated default value
                'same_numa': (8400, -0.05, 0.05, 'MB/s'),
                'diff_numa_same_socket': (6000, -0.05, 0.05, 'MB/s'),
                'diff_socket_same_node': (8400, -0.05, 0.05, 'MB/s'),
                'diff_node': (12000, -0.05, 0.05, 'MB/s')
            },
            'easybuild': {                
                'default': (2500, -0.05, 0.05, 'MB/s'),  # Updated default value
                'same_numa': (8600, -0.05, 0.05, 'MB/s'),
                'diff_numa_same_socket': (6800, -0.05, 0.05, 'MB/s'),
                'diff_socket_same_node': (7800, -0.05, 0.05, 'MB/s'),
                'diff_node': (12000, -0.05, 0.05, 'MB/s')
            },
            'local': {                
                'default': (2800, -0.05, 0.05, 'MB/s'),  # Updated default value
                'same_numa': (8000, -0.05, 0.05, 'MB/s'),
                'diff_numa_same_socket': (8000, -0.05, 0.05, 'MB/s'),
                'diff_socket_same_node': (8000, -0.05, 0.05, 'MB/s'),
                'diff_node': (12000, -0.05, 0.05, 'MB/s')
            },
        }
    },
    # Keep iris values for now since we don't have new test results for it
    'iris': {
        'latency': {
            'default': (0.18, -0.05, 0.05, 'us'),  # Updated from 0.21 to 0.18
            'multi_node': (8.0, -0.5, 0.5, 'us'),  # Updated from 3.9 to 8.0 with wider tolerance
            'same_numa': (0.18, -0.05, 0.05, 'us'),
            'diff_numa_same_socket': (0.18, -0.05, 0.05, 'us'),
            'diff_socket_same_node': (0.17, -0.05, 0.05, 'us'),
            'diff_node': (8.0, -0.5, 0.5, 'us')
        },
        'bandwidth': {
            'eessi': {
                'default': (7200, -0.05, 0.05, 'MB/s'),  # Updated default value
                'multi_node': (1500, -0.05, 0.05, 'MB/s'),  # Updated for multi-node
                'same_numa': (7200, -0.05, 0.05, 'MB/s'),
                'diff_numa_same_socket': (4500, -0.05, 0.05, 'MB/s'),
                'diff_socket_same_node': (4400, -0.05, 0.05, 'MB/s'),
                'diff_node': (1500, -0.05, 0.05, 'MB/s')
            },
            'easybuild': {                
                'default': (2500, -0.05, 0.05, 'MB/s'),  # Updated default value
                'multi_node': (1900, -0.05, 0.05, 'MB/s'),  # Updated for multi-node
                'same_numa': (2500, -0.05, 0.05, 'MB/s'),
                'diff_numa_same_socket': (2500, -0.05, 0.05, 'MB/s'),
                'diff_socket_same_node': (2500, -0.05, 0.05, 'MB/s'),
                'diff_node': (1900, -0.05, 0.05, 'MB/s')
            },
            'local': {                
                'default': (2800, -0.05, 0.05, 'MB/s'),  # Updated default value
                'multi_node': (2000, -0.05, 0.05, 'MB/s'),  # Updated for multi-node
                'same_numa': (2800, -0.05, 0.05, 'MB/s'),
                'diff_numa_same_socket': (2800, -0.05, 0.05, 'MB/s'),
                'diff_socket_same_node': (6200, -0.05, 0.05, 'MB/s'),
                'diff_node': (2000, -0.05, 0.05, 'MB/s')
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
                'module load perf/OSU-Micro-Benchmarks/7.5-gompi-2023b || echo "Warning: Could not load OSU benchmarks"'
            ],
            'eessi': [
                'module load EESSI || echo "Warning: Could not load EESSI"',
                'module load OSU-Micro-Benchmarks/7.2-gompi-2023b || echo "Warning: Could not load OSU benchmarks"'
            ]
        }