import os
import numpy as np
import matplotlib.pyplot as plt

# Define the path to your data folder
# This assumes this script is next to the 'data' folder
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def inspect_npy(filename):
    path = os.path.join(DATA_DIR, filename)
    
    if not os.path.exists(path):
        print(f"[-] File not found: {filename}")
        print(f"    (Looked in: {path})")
        return None

    print(f"\n[+] Inspecting: {filename}")
    try:
        data = np.load(path)
        print(f"    Shape: {data.shape}  (Total items)")
        print(f"    Type:  {data.dtype}")
        print(f"    Min:   {np.min(data)}")
        print(f"    Max:   {np.max(data)}")
        print(f"    First 10 values: {data[:10]}")
        return data
    except Exception as e:
        print(f"    Failed to load: {e}")
        return None

if __name__ == "__main__":
    print(f"Searching in directory: {DATA_DIR}")
    
    # 1. Load the timing traces
    traces = inspect_npy("live_traces.npy")

    # 2. Load the inputs (plaintexts)
    inspect_npy("live_plaintexts.npy")

    # 3. Interactive Visualization
    if traces is not None:
        print("\n[?] Visualization Configuration:")
        total_traces = len(traces)
        
        # Input: Start Index
        try:
            start_str = input(f"    Start index (0-{total_traces-1}) [Default: 0]: ")
            start_idx = int(start_str) if start_str.strip() else 0
        except ValueError:
            print("    [-] Invalid input. Defaulting to 0.")
            start_idx = 0
            
        # Input: Count
        try:
            count_str = input(f"    Number of traces to view [Default: 200]: ")
            view_count = int(count_str) if count_str.strip() else 200
        except ValueError:
            print("    [-] Invalid input. Defaulting to 200.")
            view_count = 200

        # Validate bounds
        if start_idx < 0: start_idx = 0
        if start_idx >= total_traces: start_idx = total_traces - 1
        
        end_idx = start_idx + view_count
        if end_idx > total_traces:
            end_idx = total_traces
            
        # Slice the data based on user input
        subset = traces[start_idx:end_idx]
        x_axis = range(start_idx, end_idx)
        
        print(f"\n[+] Generating plot for traces {start_idx} to {end_idx}...")
        
        # Create a figure with 2 subplots (stacked vertically)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Plot 1: Standard Line Plot (Reverted from Scatter)
        ax1.plot(x_axis, subset, linewidth=1.5, color='#3498db', label='Trace Timing')
        ax1.set_title(f"Timeline View: Traces {start_idx} - {end_idx}")
        ax1.set_ylabel("Cycles")
        ax1.set_xlabel("Trace Index")
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Plot 2: Histogram of the selected subset
        ax2.hist(subset, bins=50, color='#2ecc71', alpha=0.7, edgecolor='black')
        ax2.set_title(f"Distribution of Access Times (Subset: {len(subset)} samples)")
        ax2.set_ylabel("Frequency")
        ax2.set_xlabel("Cycles")
        ax2.axvline(x=100, color='red', linestyle='--', label='Threshold')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        plt.show()