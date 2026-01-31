#!/usr/bin/env python3
"""
Advanced Cache Side-Channel Simulation (Flush+Reload) - ANIMATED MODE

This module simulates a CPU cache timing attack using Matplotlib's
FuncAnimation for smooth, real-time visualization.
"""

from pathlib import Path
from typing import Tuple
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class CacheTimeSimulator:
    """Simulates CPU cache timing behavior using vectorized operations."""

    def __init__(self, hit_cycles: float = 45.0, miss_cycles: float = 180.0, 
                 noise_std: float = 5.0):
        self.hit_cycles = hit_cycles
        self.miss_cycles = miss_cycles
        self.noise_std = noise_std

    def simulate_batch(self, num_samples: int, secret_key: int, 
                       monitored_index: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Vectorized simulation of a small batch of traces.
        """
        # 1. Generate random inputs (Plaintext)
        plaintexts = np.random.randint(0, 256, num_samples, dtype=np.uint8)

        # 2. Simulate Victim Logic: SBox[Plaintext XOR Key]
        accessed_indices = plaintexts ^ secret_key

        # 3. Initialize timings with "Miss" latency (base case)
        timings = np.full(num_samples, self.miss_cycles)

        # 4. Apply "Hit" latency where the victim accessed our monitored line
        hits_mask = (accessed_indices == monitored_index)
        timings[hits_mask] = self.hit_cycles

        # 5. Add Gaussian Noise (Jitter)
        noise = np.random.normal(0, self.noise_std, num_samples)
        timings = timings + noise

        # 6. Clip to ensure no negative time cycles
        timings = np.maximum(0, timings)

        return plaintexts, timings

class CacheAttacker:
    """Analyzes timing traces to recover the secret key."""

    @staticmethod
    def recover_key(plaintexts: np.ndarray, timings: np.ndarray, 
                    monitored_index: int, threshold: float = 100.0) -> Tuple[int, float]:
        """
        Attempts to recover the key by analyzing correlation between 
        low timing (Hits) and input plaintexts.
        """
        # 1. Filter for Fast Traces (Cache Hits)
        hit_mask = timings < threshold
        fast_plaintexts = plaintexts[hit_mask]

        if len(fast_plaintexts) == 0:
            return -1, 0.0 # Not enough data yet

        # 2. Key Hypothesis: Key == (Plaintext XOR Monitored_Index)
        key_guesses = fast_plaintexts ^ monitored_index

        # 3. Vote for the most common key
        counts = np.bincount(key_guesses, minlength=256)
        likely_key = np.argmax(counts)
        confidence = counts[likely_key] / len(key_guesses)

        return int(likely_key), confidence

class LiveSimulation:
    """Manages the simulation state, animation, and data storage."""
    
    def __init__(self, secret_key=0x5A, monitored_index=94, duration=10):
        self.secret_key = secret_key
        self.monitored_index = monitored_index
        self.duration = duration
        
        # Components
        self.sim = CacheTimeSimulator(hit_cycles=45, miss_cycles=180, noise_std=5)
        
        # Data Storage
        self.all_plaintexts = []
        self.all_timings = []
        self.start_time = None
        self.is_running = True
        
        # Matplotlib Setup
        # Use 'nbAgg' if running in Jupyter, otherwise default is fine
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Window Title handling (backend dependent)
        try:
            self.fig.canvas.manager.set_window_title("Live Side-Channel Attack Simulator")
        except AttributeError:
            pass # Some backends don't support this
            
        self.ani = None 
        
        # Setup Plots
        self._setup_plots()

    def _setup_plots(self):
        """Initializes the plot lines and labels."""
        # Plot 1: Rolling Trace View
        self.line_plot, = self.ax1.plot([], [], color='#3498db', lw=1, alpha=0.8)
        self.ax1.axhline(y=100, color='red', linestyle='--', alpha=0.5)
        self.ax1.set_title("Live Timing Feed (Last 100 Traces)")
        self.ax1.set_ylabel("Cycles")
        self.ax1.set_ylim(0, 300)
        self.ax1.set_xlim(0, 100)
        self.ax1.grid(True, alpha=0.3)

        # Plot 2: Cumulative Histogram
        self.ax2.set_title("Cumulative Distribution")
        self.ax2.set_xlabel("Cycles")
        self.ax2.set_ylabel("Frequency")
        self.ax2.grid(True, alpha=0.3)

    # --- FIX IS HERE: Added 'frame' argument ---
    def update(self, frame):
        """Animation callback function."""
        
        # Check Timer
        if self.start_time is None:
            self.start_time = time.time()
            
        elapsed = time.time() - self.start_time
        
        # Stop condition
        if elapsed > self.duration:
            if self.is_running:
                print("\n[*] Time limit reached. Stopping animation.")
                self.is_running = False
                self.ani.event_source.stop()
                plt.close(self.fig)
            return

        # 1. Simulate Batch
        batch_size = 50
        pt_batch, time_batch = self.sim.simulate_batch(
            batch_size, self.secret_key, self.monitored_index
        )
        
        # 2. Store Data
        self.all_plaintexts.append(pt_batch)
        self.all_timings.append(time_batch)
        
        # 3. Prepare Analysis Data
        flat_pt = np.concatenate(self.all_plaintexts)
        flat_time = np.concatenate(self.all_timings)
        
        # 4. Run Attack Logic
        rec_key, conf = CacheAttacker.recover_key(flat_pt, flat_time, self.monitored_index)
        
        # 5. Update Plots
        # -- Update Line --
        display_data = flat_time[-100:]
        self.line_plot.set_data(range(len(display_data)), display_data)
        
        # -- Update Histogram (Clear and redraw) --
        self.ax2.clear()
        self.ax2.hist(flat_time, bins=50, color='#2ecc71', 
                     edgecolor='black', alpha=0.7)
        self.ax2.axvline(x=100, color='red', linestyle='--', label='Threshold')
        self.ax2.set_title("Cumulative Distribution")
        self.ax2.grid(True, alpha=0.3)
        self.ax2.legend(loc='upper right')
        
        # -- Update Title --
        status = "WORKING..." if conf < 0.9 else "CRACKED!"
        self.fig.suptitle(
            f"Time: {elapsed:.1f}s | Status: {status} | Traces: {len(flat_time)} | "
            f"Guess: {hex(rec_key)} ({conf:.1%})", 
            fontsize=16, fontweight='bold'
        )

    def run(self):
        """Starts the animation loop."""
        print(f"[*] Starting Live Simulation. Target Key: {hex(self.secret_key)}")
        print(f"[*] Will stop automatically after {self.duration} seconds.")
        
        self.ani = animation.FuncAnimation(
            self.fig, self.update, interval=50, cache_frame_data=False
        )
        plt.show() # Blocks here
        
        # This runs after the window closes
        self.save_data()

    def save_data(self):
        """Saves collected data to disk."""
        base_dir = Path(__file__).parent.absolute()
        data_dir = base_dir / "data"
        data_dir.mkdir(exist_ok=True)
        
        if self.all_timings:
            flat_pt = np.concatenate(self.all_plaintexts)
            flat_time = np.concatenate(self.all_timings)
            
            np.save(data_dir / "live_traces.npy", flat_time)
            np.save(data_dir / "live_plaintexts.npy", flat_pt)
            print(f"\n[*] Saved {len(flat_time)} traces to {data_dir}")
        else:
            print("\n[*] No data generated.")

if __name__ == "__main__":
    sim_app = LiveSimulation(duration=10)
    try:
        sim_app.run()
    except KeyboardInterrupt:
        print("\n[*] Interrupted by user.")
        # Attempt to save if interrupted
        sim_app.save_data()
        sys.exit(0)