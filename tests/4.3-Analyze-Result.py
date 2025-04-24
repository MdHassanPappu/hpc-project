#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import os

# Load the CSV file
csv_file = os.path.expanduser('~/hpc-project/osu_perf_results.csv')
df = pd.read_csv(csv_file)

# Group by binding type and binary source for bandwidth
bw_df = df[df['metric'] == 'bandwidth'].copy()
pivot = pd.pivot_table(bw_df, 
                     values='value', 
                     index='binding_type',
                     columns='binary_source', 
                     aggfunc='mean')

# Plot
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