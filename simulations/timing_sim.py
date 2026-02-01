#!/usr/bin/env python3
"""
Advanced Timing Side-Channel Simulation (Early Exit) - ANIMATED MODE

This module simulates a password timing attack using Matplotlib's
FuncAnimation to visualize the 'Staircase Effect' in real-time.
"""

from pathlib import Path
import sys
import time
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class TimingSimulator:
    """Simulates the vulnerable password check."""

    def __init__(self, base_time: float = 100.0, char_delay: float = 20.0, 
                 jitter_std: float = 5.0):
        self.base_time = base_time
        self.char_delay = char_delay
        self.jitter_std = jitter_std

    def vulnerable_compare(self, secret: str, user_input: str) -> float:
        """
        Simulate a vulnerable string comparison with 'Early Exit'.
        Returns: Execution time.
        """
        execution_time = self.base_time
        min_len = min(len(secret), len(user_input))
        
        for i in range(min_len):
            execution_time += self.char_delay
            # The Vulnerability: Early Exit
            if secret[i] != user_input[i]:
                break
                
        # Add Jitter
        noise = np.random.normal(0, self.jitter_std)
        return max(0, execution_time + noise)

    def generate_batch(self, batch_size: int, secret_pwd: str):
        """Generates a batch of guesses and measures their time."""
        inputs = []
        timings = []
        correct_counts = []
        
        for _ in range(batch_size):
            # 50% Random Junk / 50% "Cheating" (Correct Prefix)
            # We do this to force the 'Staircase' pattern to appear on screen
            if random.random() < 0.5:
                guess = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=len(secret_pwd)))
            else:
                match_len = random.randint(0, len(secret_pwd))
                prefix = secret_pwd[:match_len]
                suffix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=len(secret_pwd)-match_len))
                guess = prefix + suffix
            
            # Measure Time
            t = self.vulnerable_compare(secret_pwd, guess)
            
            # Calculate Label (How many correct?)
            match_count = 0
            for i in range(min(len(secret_pwd), len(guess))):
                if secret_pwd[i] == guess[i]:
                    match_count += 1
                else:
                    break
            
            inputs.append(guess)
            timings.append(t)
            correct_counts.append(match_count)
            
        return inputs, timings, correct_counts

class LiveTimingApp:
    """Manages the live timing attack visualization."""

    def __init__(self, secret_pwd="admin", duration=15):
        self.secret_pwd = secret_pwd
        self.duration = duration
        
        # Simulator
        self.sim = TimingSimulator(base_time=100, char_delay=20, jitter_std=5)
        
        # Data Storage
        self.all_timings = []
        self.all_counts = []
        self.start_time = None
        self.is_running = True
        
        # Matplotlib Setup
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        try:
            self.fig.canvas.manager.set_window_title("Live Timing Attack Simulator")
        except: pass

        self.scat = None # Placeholder for scatter plot
        self._setup_plots()

    def _setup_plots(self):
        """Initializes the scatter plot."""
        # Initialize with empty data
        self.scat = self.ax.scatter([], [], alpha=0.6, c=[], cmap='viridis', 
                                   edgecolors='k', s=50, vmin=0, vmax=len(self.secret_pwd))
        
        self.ax.set_title(f"Live Timing Leakage: Target '{self.secret_pwd}'")
        self.ax.set_xlabel("Correct Characters (Prefix)")
        self.ax.set_ylabel("Execution Time (ms)")
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlim(-0.5, len(self.secret_pwd) + 0.5)
        self.ax.set_ylim(80, 100 + (len(self.secret_pwd) * 30)) # Auto-scale Y axis
        self.ax.set_xticks(range(len(self.secret_pwd) + 1))

    def update(self, frame):
        """Animation Loop."""
        if self.start_time is None: self.start_time = time.time()
        elapsed = time.time() - self.start_time
        
        # Stop Condition
        if elapsed > self.duration:
            if self.is_running:
                print("\n[*] Simulation finished.")
                self.is_running = False
                self.ani.event_source.stop()
                plt.close(self.fig)
            return

        # 1. Generate Data (Small batch per frame)
        _, times, counts = self.sim.generate_batch(10, self.secret_pwd)
        
        # 2. Store Data
        self.all_timings.extend(times)
        self.all_counts.extend(counts)
        
        # 3. Update Scatter Plot
        # Matplotlib requires (x, y) coordinates as a 2D array
        data = np.c_[self.all_counts, self.all_timings]
        self.scat.set_offsets(data)
        self.scat.set_array(np.array(self.all_counts)) # Update colors based on X value
        
        # Update Title
        self.ax.set_title(f"Live Attack | Samples: {len(self.all_timings)} | Time: {elapsed:.1f}s")

    def run(self):
        print(f"[*] Starting Live Timing Attack on '{self.secret_pwd}'")
        print(f"[*] Duration: {self.duration} seconds")
        
        self.ani = animation.FuncAnimation(
            self.fig, self.update, interval=50, cache_frame_data=False
        )
        plt.show()
        self.save_data()

    def save_data(self):
        base_dir = Path(__file__).parent.absolute()
        data_dir = base_dir / "data"
        data_dir.mkdir(exist_ok=True)
        
        if self.all_timings:
            np.save(data_dir / "live_timing_traces.npy", self.all_timings)
            np.save(data_dir / "live_timing_labels.npy", self.all_counts)
            print(f"\n[*] Saved {len(self.all_timings)} traces to {data_dir}")

if __name__ == "__main__":
    # You can change the password here to test different lengths
    app = LiveTimingApp(secret_pwd="admin", duration=10)
    try:
        app.run()
    except KeyboardInterrupt:
        app.save_data()
        sys.exit(0)