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


print("Analysis complete. Check the generated PNG files.")