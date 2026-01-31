import numpy as np
import os

# Define the path to your data folder
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def inspect_npy(filename):
    path = os.path.join(DATA_DIR, filename)
    
    if not os.path.exists(path):
        print(f"❌ Error: File not found at {path}")
        return

    print(f"\n🔍 Inspecting: {filename}")
    try:
        data = np.load(path)
        print(f"   Shape: {data.shape}  <-- (Rows, Columns)")
        print(f"   Type:  {data.dtype}")
        print(f"   First 5 samples:\n{data[:5]}")
    except Exception as e:
        print(f"   ❌ Failed to load: {e}")

if __name__ == "__main__":
    # Check both files
    inspect_npy("cache_traces.npy")
    inspect_npy("cache_labels.npy")