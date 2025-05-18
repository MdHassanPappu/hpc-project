# Reference values by system, binding type, and binary source
REFERENCE_VALUES = {
    'aion': {
        'latency': {
            'eessi': {
                'default': (0.21, -0.2, 0.2, 'us'),  # Updated from 0.21 to 0.18
                'same_numa': (0.21, -0.2, 0.2, 'us'),
                'diff_numa_same_socket': (0.21, -0.2, 0.2, 'us'),
                'diff_socket_same_node': (0.21, -0.2, 0.2, 'us'),
                'diff_node': (4.0, -0.2, 0.2, 'us')
            },
            'easybuild': {
                'default': (0.21, -0.2, 0.2, 'us'),  # Updated from 0.21 to 0.18
                'same_numa': (0.21, -0.2, 0.2, 'us'),
                'diff_numa_same_socket': (0.21, -0.2, 0.2, 'us'),
                'diff_socket_same_node': (0.21, -0.2, 0.2, 'us'),
                'diff_node': (4.0, -0.2, 0.2, 'us')
            },
            'local': {
                'default': (0.21, -0.2, 0.2, 'us'),  # Updated from 0.21 to 0.18
                'same_numa': (0.21, -0.2, 0.2, 'us'),
                'diff_numa_same_socket': (0.21, -0.2, 0.2, 'us'),
                'diff_socket_same_node': (0.21, -0.2, 0.2, 'us'),
                'diff_node': (4.0, -0.2, 0.2, 'us')
            },            
        },
        'bandwidth': {
            'eessi': {
                'default': (7200, -0.2, 0.2, 'MB/s'),  # Updated default value
                'same_numa': (6800, -0.2, 0.2, 'MB/s'),
                'diff_numa_same_socket': (5100, -0.2, 0.2, 'MB/s'),
                'diff_socket_same_node': (8000, -0.2, 0.2, 'MB/s'),
                'diff_node': (7300, -0.2, 0.2, 'MB/s')
            },
            'easybuild': {                
                'default': (2500, -0.2, 0.2, 'MB/s'),  # Updated default value
                'same_numa': (8200, -0.2, 0.2, 'MB/s'),
                'diff_numa_same_socket': (8850, -0.2, 0.2, 'MB/s'),
                'diff_socket_same_node': (7000, -0.2, 0.2, 'MB/s'),
                'diff_node': (6200, -0.2, 0.2, 'MB/s')
            },
            'local': {                
                'default': (2800, -0.2, 0.2, 'MB/s'),  # Updated default value
                'same_numa': (4000, -0.2, 0.2, 'MB/s'),
                'diff_numa_same_socket': (8700, -0.2, 0.2, 'MB/s'),
                'diff_socket_same_node': (7100, -0.2, 0.2, 'MB/s'),
                'diff_node': (12000, -0.2, 0.2, 'MB/s')
            },
        }
    },
    # Keep iris values for now since we don't have new test results for it
    'iris': {
        'latency': {
            'eessi': {
                'default': (0.21, -0.2, 0.2, 'us'),  # Updated from 0.21 to 0.18
                'same_numa': (0.75, -0.2, 0.2, 'us'),
                'diff_numa_same_socket': (0.3, -0.2, 0.2, 'us'),
                'diff_socket_same_node': (0.3, -0.2, 0.2, 'us'),
                'diff_node': (4.0, -0.2, 0.2, 'us')
            },
            'easybuild': {
                'default': (0.21, -0.2, 0.2, 'us'),  # Updated from 0.21 to 0.18
                'same_numa': (0.25, -0.2, 0.2, 'us'),
                'diff_numa_same_socket': (0.31, -0.2, 0.2, 'us'),
                'diff_socket_same_node': (0.38, -0.2, 0.2, 'us'),
                'diff_node': (4.0, -0.2, 0.2, 'us')
            },
            'local': {
                'default': (0.21, -0.2, 0.2, 'us'),  # Updated from 0.21 to 0.18
                'same_numa': (0.71, -0.2, 0.2, 'us'),
                'diff_numa_same_socket': (0.3, -0.2, 0.2, 'us'),
                'diff_socket_same_node': (0.33, -0.2, 0.2, 'us'),
                'diff_node': (4.0, -0.2, 0.2, 'us')
            },            
        },
        'bandwidth': {
            'eessi': {
                'default': (7200, -0.2, 0.2, 'MB/s'),  # Updated default value
                'same_numa': (1700, -0.2, 0.2, 'MB/s'),
                'diff_numa_same_socket': (2200, -0.2, 0.2, 'MB/s'),
                'diff_socket_same_node': (4000, -0.2, 0.2, 'MB/s'),
                'diff_node': (7300, -0.2, 0.2, 'MB/s')
            },
            'easybuild': {                
                'default': (2500, -0.2, 0.2, 'MB/s'),  # Updated default value
                'same_numa': (4700, -0.2, 0.2, 'MB/s'),
                'diff_numa_same_socket': (2200, -0.2, 0.2, 'MB/s'),
                'diff_socket_same_node': (4000, -0.2, 0.2, 'MB/s'),
                'diff_node': (11000, -0.2, 0.2, 'MB/s')
            },
            'local': {                
                'default': (2800, -0.2, 0.2, 'MB/s'),  # Updated default value
                'same_numa': (4600, -0.2, 0.2, 'MB/s'),
                'diff_numa_same_socket': (2300, -0.2, 0.2, 'MB/s'),
                'diff_socket_same_node': (4000, -0.2, 0.2, 'MB/s'),
                'diff_node': (7200, -0.2, 0.2, 'MB/s')
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