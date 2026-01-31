import multiprocessing
import os
import sys

# Define the scripts we want to run
SCRIPTS = [
    "cache_sim.py",         # The Live Cache Attack
    "live_timing_sim.py",   # The Live Timing Staircase
    "hamming_power_sim.py"  # The Live Power Trace
]

def run_script(script_name):
    """Worker function to run a single script."""
    print(f"[*] Launching {script_name}...")
    # Using os.system or subprocess is easiest here to spawn a new window
    # logic depends on OS, but for simple python scripts:
    os.system(f"{sys.executable} {script_name}")

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 AEGIS MASTER LAUNCHER: STARTING ALL SIMULATIONS")
    print("=" * 50)
    
    processes = []

    # Create a process for each script
    for script in SCRIPTS:
        p = multiprocessing.Process(target=run_script, args=(script,))
        p.start()
        processes.append(p)
        
    print(f"\n[+] All {len(SCRIPTS)} simulations running.")
    print("[!] Close the popup windows to stop them.")
    
    # Wait for all to finish
    for p in processes:
        p.join()
        
    print("\n[=] All simulations finished.")