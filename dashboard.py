#!/usr/bin/env python3
"""
AEGIS MASTER DASHBOARD (2x2 Layout)
Integrates Cache, Timing, and Detailed Power analysis into a single view.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

# ==========================================
# 1. SIMULATION LOGIC
# ==========================================

class CacheSim:
    def get_batch(self, size=10):
        # Mostly misses (180), rare hits (45)
        timings = np.full(size, 180.0)
        hits = np.random.choice([True, False], size, p=[0.15, 0.85])
        timings[hits] = 45.0
        # Add noise
        timings += np.random.normal(0, 5, size)
        return timings

class TimingSim:
    def __init__(self, pwd="admin"):
        self.pwd = pwd
    
    def get_batch(self, size=5):
        times = []
        counts = []
        for _ in range(size):
            # 50% chance to simulate a correct prefix guess
            if random.random() < 0.5:
                match = random.randint(0, len(self.pwd))
            else:
                match = 0 # Wrong guess
            
            # Base 100ms + 20ms per correct char + Noise
            t = 100 + (20 * match) + np.random.normal(0, 5)
            times.append(t)
            counts.append(match)
        return times, counts

class PowerSim:
    def get_batch(self, size=10):
        weights = np.random.randint(0, 9, size) # Hamming weights (0-8)
        # Power = Base(1) + Leak(0.5 * Weight) + Noise
        power = 1.0 + (0.5 * weights) + np.random.normal(0, 0.2, size)
        return weights, power

# ==========================================
# 2. DASHBOARD APPLICATION
# ==========================================

class AegisDashboard:
    def __init__(self):
        # Create a 2x2 Grid Layout
        self.fig, self.axs = plt.subplots(2, 2, figsize=(14, 10))
        self.fig.canvas.manager.set_window_title("AEGIS Side-Channel Dashboard")
        self.fig.suptitle("AEGIS: Integrated Side-Channel Analysis Platform", fontsize=16, fontweight='bold')
        
        # Unpack the axes for easier naming
        # Top-Left, Top-Right, Bottom-Left, Bottom-Right
        self.ax_cache = self.axs[0, 0]
        self.ax_time = self.axs[0, 1]
        self.ax_pwr_trace = self.axs[1, 0]
        self.ax_pwr_corr = self.axs[1, 1]

        # --- 1. CACHE ATTACK (Top-Left) ---
        self.cache_sim = CacheSim()
        self.cache_data = []
        self.line_cache, = self.ax_cache.plot([], [], color='#3498db', lw=1.5)
        self.ax_cache.set_title("1. CACHE: Flush+Reload Trace")
        self.ax_cache.set_ylabel("CPU Cycles")
        self.ax_cache.set_ylim(0, 250)
        self.ax_cache.set_xlim(0, 100)
        self.ax_cache.axhline(100, color='red', linestyle='--', alpha=0.5)
        self.ax_cache.grid(True, alpha=0.3)

        # --- 2. TIMING ATTACK (Top-Right) ---
        self.timing_sim = TimingSim()
        self.time_vals = []
        self.time_counts = []
        self.scat_time = self.ax_time.scatter([], [], c=[], cmap='viridis', edgecolors='k', alpha=0.7)
        self.ax_time.set_title("2. TIMING: Execution Time vs Correctness")
        self.ax_time.set_ylabel("Time (ms)")
        self.ax_time.set_xlabel("Correct Characters (Prefix)")
        self.ax_time.set_xlim(-0.5, 5.5)
        self.ax_time.set_ylim(80, 250)
        self.ax_time.grid(True, alpha=0.3)

        # --- 3. POWER TRACE (Bottom-Left) ---
        self.power_sim = PowerSim()
        self.pwr_vals = []
        self.pwr_weights = []
        self.line_pwr, = self.ax_pwr_trace.plot([], [], color='#e74c3c', lw=1.5)
        self.ax_pwr_trace.set_title("3. POWER: Live Consumption Trace")
        self.ax_pwr_trace.set_ylabel("Power (Arbitrary Units)")
        self.ax_pwr_trace.set_ylim(0, 8)
        self.ax_pwr_trace.set_xlim(0, 100)
        self.ax_pwr_trace.grid(True, alpha=0.3)

        # --- 4. POWER CORRELATION (Bottom-Right) ---
        self.scat_pwr = self.ax_pwr_corr.scatter([], [], color='#e74c3c', alpha=0.6, edgecolors='k')
        self.ax_pwr_corr.set_title("4. POWER: Hamming Weight Correlation")
        self.ax_pwr_corr.set_xlabel("Hamming Weight (Bits)")
        self.ax_pwr_corr.set_ylabel("Measured Power")
        self.ax_pwr_corr.set_xlim(-0.5, 8.5)
        self.ax_pwr_corr.set_ylim(0, 8)
        self.ax_pwr_corr.grid(True, alpha=0.3)

    def update(self, frame):
        # Update Cache (Top Left)
        new_cache = self.cache_sim.get_batch(5)
        self.cache_data.extend(new_cache)
        if len(self.cache_data) > 100: self.cache_data = self.cache_data[-100:]
        self.line_cache.set_data(range(len(self.cache_data)), self.cache_data)

        # Update Timing (Top Right)
        t_vals, t_counts = self.timing_sim.get_batch(5)
        self.time_vals.extend(t_vals)
        self.time_counts.extend(t_counts)
        if len(self.time_vals) > 200: # Limit history
            self.time_vals = self.time_vals[-200:]
            self.time_counts = self.time_counts[-200:]
        self.scat_time.set_offsets(np.c_[self.time_counts, self.time_vals])
        self.scat_time.set_array(np.array(self.time_counts))

        # Update Power (Bottom Left & Right)
        p_weights, p_vals = self.power_sim.get_batch(5)
        self.pwr_vals.extend(p_vals)
        self.pwr_weights.extend(p_weights)
        
        # Update Line (Trace)
        disp_pwr = self.pwr_vals[-100:]
        self.line_pwr.set_data(range(len(disp_pwr)), disp_pwr)
        
        # Update Scatter (Correlation)
        if len(self.pwr_vals) > 200:
            corr_vals = self.pwr_vals[-200:]
            corr_weights = self.pwr_weights[-200:]
        else:
            corr_vals = self.pwr_vals
            corr_weights = self.pwr_weights
            
        self.scat_pwr.set_offsets(np.c_[corr_weights, corr_vals])

    def run(self):
        print("[*] Launching 2x2 Dashboard...")
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=50, cache_frame_data=False)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    app = AegisDashboard()
    app.run()