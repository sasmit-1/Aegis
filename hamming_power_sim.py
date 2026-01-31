#!/usr/bin/env python3
"""
Hamming Weight Power Simulation - ANIMATED MODE

This module simulates power consumption in real-time, showing how
the number of active bits (Hamming Weight) directly impacts power usage.
"""

from pathlib import Path
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class HammingPowerSimulator:
    """Simulates power consumption based on Hamming weight and transitions."""
    
    def __init__(self, bit_width: int = 8, base_power: float = 1.0, 
                 transition_power: float = 0.5, leakage_power: float = 0.1):
        self.bit_width = bit_width
        self.base_power = base_power
        self.transition_power = transition_power
        self.leakage_power = leakage_power
        self.previous_value = 0
        
    def hamming_weight(self, value: int) -> int:
        return bin(value).count('1')
    
    def hamming_distance(self, val1: int, val2: int) -> int:
        return self.hamming_weight(val1 ^ val2)
    
    def calculate_power(self, current_value: int) -> float:
        # Calculate Hamming distance (bit transitions from previous state)
        transitions = self.hamming_distance(current_value, self.previous_value)
        
        # Calculate Hamming weight (active bits)
        active_bits = self.hamming_weight(current_value)
        
        # Power model
        power = (self.base_power + 
                 self.leakage_power * active_bits + 
                 self.transition_power * transitions)
        
        self.previous_value = current_value
        return power

    def generate_batch(self, batch_size=10):
        """Generates a small batch of random data and power readings."""
        data_seq = []
        power_seq = []
        weight_seq = []
        
        max_val = (1 << self.bit_width) - 1
        
        for _ in range(batch_size):
            val = np.random.randint(0, max_val + 1)
            pwr = self.calculate_power(val)
            weight = self.hamming_weight(val)
            
            data_seq.append(val)
            power_seq.append(pwr)
            weight_seq.append(weight)
            
        return data_seq, power_seq, weight_seq

class LivePowerApp:
    """Manages the live power simulation visualization."""

    def __init__(self, duration=10):
        self.duration = duration
        
        # Components
        self.sim = HammingPowerSimulator()
        
        # Data Storage
        self.all_power = []
        self.all_weights = []
        self.start_time = None
        self.is_running = True
        
        # Matplotlib Setup: Create 2 Subplots (Top and Bottom)
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        try:
            self.fig.canvas.manager.set_window_title("Live Power Analysis Simulator")
        except: pass
        
        self._setup_plots()

    def _setup_plots(self):
        """Initializes the plots."""
        # --- Top Plot: Power Trace (Line) ---
        self.line_power, = self.ax1.plot([], [], color='#e74c3c', lw=2, label='Power Consumption')
        self.ax1.set_title("1. Live Power Trace (Side-Channel Leakage)")
        self.ax1.set_ylabel("Power (Arbitrary Units)")
        self.ax1.set_xlim(0, 100)
        self.ax1.set_ylim(0, 10) 
        self.ax1.grid(True, alpha=0.3)
        self.ax1.legend(loc='upper right')

        # --- Bottom Plot: Correlation (Scatter) ---
        self.scat_corr = self.ax2.scatter([], [], alpha=0.6, c=[], cmap='viridis', edgecolors='k')
        self.ax2.set_title("2. Correlation: Hamming Weight vs. Power")
        self.ax2.set_xlabel("Hamming Weight (Number of 1s)")
        self.ax2.set_ylabel("Measured Power")
        self.ax2.set_xlim(-0.5, 8.5) # 8-bit bus = max 8 ones
        self.ax2.set_ylim(0, 10)
        self.ax2.grid(True, alpha=0.3)

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

        # 1. Generate Data
        _, pwr_batch, weight_batch = self.sim.generate_batch(5)
        
        # 2. Store Data
        self.all_power.extend(pwr_batch)
        self.all_weights.extend(weight_batch)
        
        # 3. Update Top Plot (Scrolling Trace)
        display_power = self.all_power[-100:] # Show last 100 samples
        self.line_power.set_data(range(len(display_power)), display_power)
        
        # 4. Update Bottom Plot (Correlation)
        # We maintain a buffer of the last 200 points for the scatter plot
        corr_weights = self.all_weights[-200:]
        corr_power = self.all_power[-200:]
        
        # Scatter plots need (x, y) coordinates combined
        self.scat_corr.set_offsets(np.c_[corr_weights, corr_power])
        self.scat_corr.set_array(np.array(corr_weights)) # Color by weight
        
        # Update Title
        self.fig.suptitle(f"Live Simulation | Time: {elapsed:.1f}s | Samples: {len(self.all_power)}", 
                         fontsize=14, fontweight='bold')

    def run(self):
        print(f"[*] Starting Live Power Simulation")
        print(f"[*] Duration: {self.duration} seconds")
        
        self.ani = animation.FuncAnimation(
            self.fig, self.update, interval=50, cache_frame_data=False
        )
        plt.tight_layout() # Fixes overlap between graphs
        plt.show()
        self.save_data()

    def save_data(self):
        base_dir = Path(__file__).parent.absolute()
        data_dir = base_dir / "data"
        data_dir.mkdir(exist_ok=True)
        
        if self.all_power:
            np.save(data_dir / "live_power_trace.npy", self.all_power)
            np.save(data_dir / "live_hamming_weights.npy", self.all_weights)
            print(f"\n[*] Saved {len(self.all_power)} traces to {data_dir}")

if __name__ == "__main__":
    app = LivePowerApp(duration=10)
    try:
        app.run()
    except KeyboardInterrupt:
        app.save_data()
        sys.exit(0)