#!/usr/bin/env python3
"""
Cache Side-Channel Simulation Model

This module simulates the 'Flush+Reload' attack vector.
It models the timing difference between accessing cached data (Hits) vs RAM (Misses).
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
import time

import matplotlib.pyplot as plt
import numpy as np

class CacheTimeSimulator:
    """Simulates CPU cache timing behavior for Side-Channel Analysis."""

    def __init__(self, hit_cycles: float = 45.0, miss_cycles: float = 180.0, 
                 noise_std: float = 3.0):
        """
        Initialize the cache simulator.

        Args:
            hit_cycles: CPU cycles for a Cache Hit (L1/L2 access)
            miss_cycles: CPU cycles for a Cache Miss (RAM access)
            noise_std: Standard deviation of Gaussian noise (Jitter)
        """
        self.hit_cycles = hit_cycles
        self.miss_cycles = miss_cycles
        self.noise_std = noise_std
        # Standard AES S-Box (Rijndael)
        self.sbox = np.array([
            0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
            0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
            0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
            0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
            0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
            0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
            0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
            0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
            0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
            0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
            0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
            0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
            0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
            0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
            0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
            0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
        ])

    def calculate_timing(self, sbox_index: int, monitored_index: int) -> float:
        """
        Calculate access time for a specific memory lookup.

        Args:
            sbox_index: The S-Box index accessed by the encryption
            monitored_index: The specific cache line the attacker is watching

        Returns:
            Timing in CPU cycles (float)
        """
        # Flush+Reload Logic:
        # If the victim accesses the monitored line -> It gets cached -> We get a HIT (Fast)
        if sbox_index == monitored_index:
            base_time = self.hit_cycles
        else:
            base_time = self.miss_cycles
        
        # Add realistic hardware jitter
        noise = np.random.normal(0, self.noise_std)
        return max(0, base_time + noise)

    def simulate_attack(self, num_samples: int, secret_key: int, monitored_index: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Simulate a full attack run with random inputs.

        Returns:
            Tuple of (plaintexts, timing_trace, labels)
        """
        plaintexts = np.random.randint(0, 256, num_samples)
        traces = []
        labels = []

        for pt in plaintexts:
            # The Victim's Operation: SBox[Plaintext XOR Key]
            sbox_index = pt ^ secret_key
            
            # The Physical Leakage
            timing = self.calculate_timing(sbox_index, monitored_index)
            
            traces.append([timing])
            labels.append(sbox_index)

        return plaintexts, np.array(traces), np.array(labels)

def plot_cache_trace(timing_trace: np.ndarray, threshold: float = 100.0, 
                     title: str = "Cache Timing Trace"):
    """Plot the cache timing behavior."""
    subset = timing_trace[:100].flatten()
    
    plt.figure(figsize=(12, 6))
    
    # Plot the line and points
    plt.plot(subset, color='#2ecc71', linewidth=1.5, label='Access Time')
    plt.scatter(range(len(subset)), subset, color='black', s=15, alpha=0.6)
    
    # Add visual threshold
    plt.axhline(y=threshold, color='red', linestyle='--', alpha=0.5, label='Hit/Miss Threshold')
    
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel("Execution Cycle (Sample #)", fontsize=12)
    plt.ylabel("Access Time (CPU Cycles)", fontsize=12)
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return plt

def demonstrate_simulation():
    """Demonstrate the Cache Simulation with file exports."""
    print("=" * 60)
    print("Cache Side-Channel Simulation Demo (Flush+Reload)")
    print("=" * 60)

    # Setup Paths (Using pathlib like Ekaksh)
    base_dir = Path(__file__).parent.absolute()
    data_dir = base_dir / "data"
    traces_dir = base_dir / "traces"
    
    data_dir.mkdir(exist_ok=True)
    traces_dir.mkdir(exist_ok=True)

    # Configuration
    SIM_TRACES = 10000
    SECRET_KEY = 0x5A
    MONITORED_INDEX = 94
    
    # Initialize Simulator
    simulator = CacheTimeSimulator(hit_cycles=45.0, miss_cycles=180.0, noise_std=3.0)

    print(f"\n1. Generating {SIM_TRACES} traces...")
    print(f"   Target Key: {hex(SECRET_KEY)}")
    print(f"   Monitored Index: {MONITORED_INDEX}")

    _, traces, labels = simulator.simulate_attack(SIM_TRACES, SECRET_KEY, MONITORED_INDEX)

    # Save Data
    np.save(data_dir / "cache_traces.npy", traces)
    np.save(data_dir / "cache_labels.npy", labels)
    print(f"   ✅ Data saved to '{data_dir}'")

    # Statistics
    hits = traces[traces < 100]
    print("\n2. Trace Statistics:")
    print(f"   - Total Samples: {len(traces)}")
    print(f"   - Cache Hits (Fast): {len(hits)} (Expected ~{SIM_TRACES // 256})")
    print(f"   - Avg Miss Time: {np.mean(traces[traces > 100]):.2f} cycles")
    print(f"   - Avg Hit Time:  {np.mean(hits):.2f} cycles")

    # Plotting
    print("\n3. Generating visualization...")
    plot_cache_trace(traces, title="Cache Side-Channel Timing (Flush+Reload)")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = traces_dir / f'cache_trace_{timestamp}.png'
    plt.savefig(filename, dpi=150)
    print(f"   📈 Plot saved to '{filename}'")

    print("\n" + "=" * 60)
    print("Simulation complete!")
    print("=" * 60)

if __name__ == "__main__":
    demonstrate_simulation()