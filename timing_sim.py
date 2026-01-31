#!/usr/bin/env python3
"""
Timing Side-Channel Simulation Model

This module simulates a timing attack vulnerability where the execution time
depends on how many characters of the password are correct (Early Exit).
"""

from datetime import datetime
from pathlib import Path
from typing import Tuple, List
import time
import random

import matplotlib.pyplot as plt
import numpy as np

class TimingSimulator:
    """Simulates execution time variations based on input correctness."""

    def __init__(self, base_time: float = 100.0, char_delay: float = 20.0, 
                 jitter_std: float = 5.0):
        """
        Initialize the timing simulator.

        Args:
            base_time: Minimum execution time (overhead) in ms or cycles
            char_delay: Extra time added for each correct character found
            jitter_std: Standard deviation of random noise (network/OS jitter)
        """
        self.base_time = base_time
        self.char_delay = char_delay
        self.jitter_std = jitter_std

    def vulnerable_compare(self, secret: str, user_input: str) -> float:
        """
        Simulate a vulnerable string comparison with 'Early Exit'.
        
        Returns:
            Simulated execution time.
        """
        execution_time = self.base_time
        
        # Determine the loop length (cannot check more than the shortest string)
        min_len = min(len(secret), len(user_input))
        
        for i in range(min_len):
            # Processing a character takes time
            execution_time += self.char_delay
            
            # THE VULNERABILITY:
            # If characters don't match, we return FALSE immediately.
            # This makes wrong guesses faster than correct guesses.
            if secret[i] != user_input[i]:
                break
                
        # Add random noise (Jitter) to make it realistic/harder
        noise = np.random.normal(0, self.jitter_std)
        return max(0, execution_time + noise)

    def simulate_attack(self, num_samples: int, secret_pwd: str) -> Tuple[List[str], np.ndarray, np.ndarray]:
        """
        Generate random inputs and measure their execution times.
        """
        inputs = []
        timings = []
        correct_counts = []
        
        # We need to generate inputs that have varying degrees of correctness
        # so the graph shows the "staircase" effect clearly.
        
        for _ in range(num_samples):
            # 50% chance: Completely random junk
            if random.random() < 0.5:
                guess = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=len(secret_pwd)))
            
            # 50% chance: We "cheat" and give it a correct prefix 
            # (This simulates the attacker slowly guessing right letters)
            else:
                match_len = random.randint(0, len(secret_pwd))
                prefix = secret_pwd[:match_len]
                suffix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=len(secret_pwd)-match_len))
                guess = prefix + suffix
            
            # Measure the time
            t = self.vulnerable_compare(secret_pwd, guess)
            
            # Calculate how many chars were actually correct (for the graph label)
            match_count = 0
            for i in range(min(len(secret_pwd), len(guess))):
                if secret_pwd[i] == guess[i]:
                    match_count += 1
                else:
                    break
            
            inputs.append(guess)
            timings.append(t)
            correct_counts.append(match_count)

        return inputs, np.array(timings), np.array(correct_counts)

def plot_timing_trace(correct_counts: np.ndarray, timings: np.ndarray, title: str = "Timing Analysis"):
    """Plot execution time vs number of correct characters."""
    plt.figure(figsize=(10, 6))
    
    # Scatter plot: x-axis is "Correct Characters", y-axis is "Time"
    plt.scatter(correct_counts, timings, alpha=0.6, c=correct_counts, cmap='viridis', edgecolors='k', s=50)
    
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel("Number of Correct Characters (Prefix)", fontsize=12)
    plt.ylabel("Execution Time (Simulated)", fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Force X-axis to show only integers (0, 1, 2...)
    plt.xticks(range(int(max(correct_counts)) + 1))
    
    plt.tight_layout()
    return plt

def demonstrate_simulation():
    """Run the simulation and save files."""
    print("=" * 60)
    print("Timing Side-Channel Simulation Demo (Early Exit)")
    print("=" * 60)

    # Setup Paths
    base_dir = Path(__file__).parent.absolute()
    data_dir = base_dir / "data"
    traces_dir = base_dir / "traces"
    data_dir.mkdir(exist_ok=True)
    traces_dir.mkdir(exist_ok=True)

    # Configuration
    SECRET_PASSWORD = "admin"  # 5 characters
    NUM_SAMPLES = 1000         # Enough dots to see the pattern
    
    # Initialize Simulator
    simulator = TimingSimulator(base_time=100.0, char_delay=20.0, jitter_std=5.0)

    print(f"\n1. Simulating attack on password: '{SECRET_PASSWORD}'")
    print(f"   Generating {NUM_SAMPLES} guesses...")
    
    _, times, labels = simulator.simulate_attack(NUM_SAMPLES, SECRET_PASSWORD)

    # Save Data
    np.save(data_dir / "timing_traces.npy", times)
    np.save(data_dir / "timing_labels.npy", labels)
    print(f"   ✅ Data saved to '{data_dir}'")

    # Statistics
    print("\n2. Analysis (Average Time per Correct Char):")
    for i in range(len(SECRET_PASSWORD) + 1):
        subset = times[labels == i]
        if len(subset) > 0:
            print(f"   - {i} Correct Chars: ~{int(np.mean(subset))} ms (based on {len(subset)} samples)")

    # Plotting
    print("\n3. Generating visualization...")
    plot_timing_trace(labels, times, title=f"Timing Leakage for '{SECRET_PASSWORD}'")
    
    # Save image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = traces_dir / f'timing_trace_{timestamp}.png'
    plt.savefig(filename, dpi=150)
    print(f"   📈 Plot saved to '{filename}'")
    
    print("\n" + "=" * 60)
    print("Simulation complete!")
    print("=" * 60)

if __name__ == "__main__":
    demonstrate_simulation()