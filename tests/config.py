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
                'same_numa': (3600, -0.05, 0.05, 'MB/s'),
                'diff_numa_same_socket': (5100, -0.05, 0.05, 'MB/s'),
                'diff_socket_same_node': (4600, -0.05, 0.05, 'MB/s'),
                'diff_node': (7300, -0.05, 0.05, 'MB/s')
            },
            'easybuild': {                
                'default': (2500, -0.05, 0.05, 'MB/s'),  # Updated default value
                'same_numa': (3300, -0.05, 0.05, 'MB/s'),
                'diff_numa_same_socket': (3300, -0.05, 0.05, 'MB/s'),
                'diff_socket_same_node': (4200, -0.05, 0.05, 'MB/s'),
                'diff_node': (6200, -0.05, 0.05, 'MB/s')
            },
            'local': {                
                'default': (2800, -0.05, 0.05, 'MB/s'),  # Updated default value
                'same_numa': (8000, -0.05, 0.05, 'MB/s'),
                'diff_numa_same_socket': (5100, -0.05, 0.05, 'MB/s'),
                'diff_socket_same_node': (5500, -0.05, 0.05, 'MB/s'),
                'diff_node': (12000, -0.05, 0.05, 'MB/s')
            },
        }
    },
    # Keep iris values for now since we don't have new test results for it
    'iris': {
        'latency': {
            'eessi': {
                'default': (0.21, -0.05, 0.05, 'us'),  # Updated from 0.21 to 0.18
                'same_numa': (0.26, -0.05, 0.05, 'us'),
                'diff_numa_same_socket': (0.21, -0.05, 0.05, 'us'),
                'diff_socket_same_node': (0.21, -0.05, 0.05, 'us'),
                'diff_node': (6.0, -0.05, 0.05, 'us')
            },
            'easybuild': {
                'default': (0.21, -0.05, 0.05, 'us'),  # Updated from 0.21 to 0.18
                'same_numa': (0.31, -0.05, 0.05, 'us'),
                'diff_numa_same_socket': (0.21, -0.05, 0.05, 'us'),
                'diff_socket_same_node': (0.21, -0.05, 0.05, 'us'),
                'diff_node': (6.0, -0.05, 0.05, 'us')
            },
            'local': {
                'default': (0.21, -0.05, 0.05, 'us'),  # Updated from 0.21 to 0.18
                'same_numa': (0.29, -0.05, 0.05, 'us'),
                'diff_numa_same_socket': (0.21, -0.05, 0.05, 'us'),
                'diff_socket_same_node': (0.21, -0.05, 0.05, 'us'),
                'diff_node': (3.5, -0.05, 0.05, 'us')
            },            
        },
        'bandwidth': {
            'eessi': {
                'default': (7200, -0.05, 0.05, 'MB/s'),  # Updated default value
                'same_numa': (4300, -0.05, 0.05, 'MB/s'),
                'diff_numa_same_socket': (2500, -0.05, 0.05, 'MB/s'),
                'diff_socket_same_node': (4600, -0.05, 0.05, 'MB/s'),
                'diff_node': (7300, -0.05, 0.05, 'MB/s')
            },
            'easybuild': {                
                'default': (2500, -0.05, 0.05, 'MB/s'),  # Updated default value
                'same_numa': (4700, -0.05, 0.05, 'MB/s'),
                'diff_numa_same_socket': (2800, -0.05, 0.05, 'MB/s'),
                'diff_socket_same_node': (4200, -0.05, 0.05, 'MB/s'),
                'diff_node': (7300, -0.05, 0.05, 'MB/s')
            },
            'local': {                
                'default': (2800, -0.05, 0.05, 'MB/s'),  # Updated default value
                'same_numa': (4300, -0.05, 0.05, 'MB/s'),
                'diff_numa_same_socket': (2400, -0.05, 0.05, 'MB/s'),
                'diff_socket_same_node': (1600, -0.05, 0.05, 'MB/s'),
                'diff_node': (7200, -0.05, 0.05, 'MB/s')
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