#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import re

# Load the JSON file
json_file = 'reports/osu-benchmark.json'
with open(json_file, 'r') as f:
    data = json.load(f)

# Convert JSON data to DataFrame
# Adjust this part based on your JSON structure
df = pd.DataFrame(data)

# Group by binding type and binary source for bandwidth
bw_df = df[df['metric'] == 'bandwidth'].copy()
pivot = pd.pivot_table(bw_df, 
                    values='value', 
                    index='binding_type',
                    columns='binary_source', 
                    aggfunc='mean')

# Plot bandwidth
plt.figure(figsize=(12, 8))
pivot.plot(kind='bar')
plt.title('Bandwidth Performance by Binding Type')
plt.ylabel('Bandwidth (MB/s)')
plt.tight_layout()
plt.savefig('bandwidth_by_binding.png')

# Similar analysis for latency
latency_df = df[df['metric'] == 'latency'].copy()
pivot = pd.pivot_table(latency_df, 
                    values='value', 
                    index='binding_type',
                    columns='binary_source', 
                    aggfunc='mean')

plt.figure(figsize=(12, 8))
pivot.plot(kind='bar')
plt.title('Latency Performance by Binding Type')
plt.ylabel('Latency (us)')
plt.tight_layout()
plt.savefig('latency_by_binding.png')

# Check resource allocation from logs
def check_allocation(log_file, expected_nodes=None, expected_cpus=None, expected_binding=None):
    with open(log_file, 'r') as f:
        log_content = f.read()
    
    # Extract allocation info using regex patterns
    # Adjust these patterns based on your log format
    node_match = re.search(r'Allocated nodes:\s*(\d+)', log_content)
    cpu_match = re.search(r'CPUs per node:\s*(\d+)', log_content)
    binding_match = re.search(r'Binding:\s*([\w-]+)', log_content)
    
    actual = {}
    if node_match: actual['nodes'] = int(node_match.group(1))
    if cpu_match: actual['cpus'] = int(cpu_match.group(1))
    if binding_match: actual['binding'] = binding_match.group(1)
    
    # Compare with expected values
    matches = {}
    if expected_nodes: matches['nodes'] = actual.get('nodes') == expected_nodes
    if expected_cpus: matches['cpus'] = actual.get('cpus') == expected_cpus
    if expected_binding: matches['binding'] = actual.get('binding') == expected_binding
    
    return actual, matches

# Look for log files and check allocations
log_dir = 'tests/logs/'
expected_config = {
    'nodes': 2,
    'cpus': 16,
    'binding': 'core'
}

if os.path.exists(log_dir):
    for log_file in os.listdir(log_dir):
        if log_file.endswith('.log'):
            full_path = os.path.join(log_dir, log_file)
            actual, matches = check_allocation(
                full_path, 
                expected_config['nodes'],
                expected_config['cpus'],
                expected_config['binding']
            )
            print(f"Log file: {log_file}")
            print(f"  Actual allocation: {actual}")
            print(f"  Matches expected: {all(matches.values())}")
            for k, v in matches.items():
                if not v:
                    print(f"  Mismatch in {k}: expected {expected_config[k]}, got {actual.get(k)}")
            print()

print("Analysis complete. Check the generated PNG files.")