#!/usr/bin/env python3
"""
Hamming Weight Power Simulation Model

This module simulates power consumption based on Hamming weight (number of 1s in binary).
Power consumption is modeled as proportional to bit transitions and Hamming distance.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np


class HammingPowerSimulator:
    """Simulates power consumption based on Hamming weight and transitions."""
    
    def __init__(self, bit_width: int = 8, base_power: float = 1.0, 
                 transition_power: float = 0.5, leakage_power: float = 0.1):
        """
        Initialize the power simulator.
        
        Args:
            bit_width: Number of bits in the data bus
            base_power: Base power consumption (arbitrary units)
            transition_power: Power per bit transition
            leakage_power: Static leakage power
        """
        self.bit_width = bit_width
        self.base_power = base_power
        self.transition_power = transition_power
        self.leakage_power = leakage_power
        self.previous_value = 0
        
    def hamming_weight(self, value: int) -> int:
        """Calculate Hamming weight (number of 1s) of a value."""
        return bin(value).count('1')
    
    def hamming_distance(self, val1: int, val2: int) -> int:
        """Calculate Hamming distance (number of differing bits) between two values."""
        return self.hamming_weight(val1 ^ val2)
    
    def calculate_power(self, current_value: int, previous_value: Optional[int] = None) -> float:
        """
        Calculate power consumption for a given value transition.
        
        Args:
            current_value: Current data value
            previous_value: Previous data value (uses stored if None)
            
        Returns:
            Power consumption in arbitrary units
        """
        if previous_value is None:
            previous_value = self.previous_value
            
        # Calculate Hamming distance (bit transitions)
        transitions = self.hamming_distance(current_value, previous_value)
        
        # Calculate Hamming weight (active bits)
        active_bits = self.hamming_weight(current_value)
        
        # Power model: base + leakage * active_bits + transition_power * transitions
        power = (self.base_power + 
                 self.leakage_power * active_bits + 
                 self.transition_power * transitions)
        
        self.previous_value = current_value
        return power
    
    def simulate_sequence(self, data_sequence: np.ndarray, reset: bool = True) -> np.ndarray:
        """
        Simulate power consumption for a sequence of data values.
        
        Args:
            data_sequence: Array of integer values
            reset: Reset previous value to 0 before simulation
            
        Returns:
            Array of power consumption values
        """
        if reset:
            self.previous_value = 0
            
        power_trace = np.zeros(len(data_sequence))
        
        for i, value in enumerate(data_sequence):
            power_trace[i] = self.calculate_power(int(value))
            
        return power_trace
    
    def simulate_random(self, num_samples: int, seed: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulate power consumption for random data.
        
        Args:
            num_samples: Number of random samples to generate
            seed: Random seed for reproducibility
            
        Returns:
            Tuple of (data_sequence, power_trace)
        """
        if seed is not None:
            np.random.seed(seed)
            
        max_value = (1 << self.bit_width) - 1
        data_sequence = np.random.randint(0, max_value + 1, size=num_samples)
        power_trace = self.simulate_sequence(data_sequence)
        
        return data_sequence, power_trace
    
    def analyze_power_statistics(self, power_trace: np.ndarray) -> dict:
        """
        Analyze power consumption statistics.
        
        Args:
            power_trace: Array of power consumption values
            
        Returns:
            Dictionary with statistical metrics
        """
        return {
            'mean': np.mean(power_trace),
            'std': np.std(power_trace),
            'min': np.min(power_trace),
            'max': np.max(power_trace),
            'median': np.median(power_trace),
            'total_energy': np.sum(power_trace)
        }


def plot_power_trace(data_sequence: np.ndarray, power_trace: np.ndarray, 
                     title: str = "Power Consumption Trace"):
    """Plot power consumption trace with data values."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Plot data sequence
    ax1.step(range(len(data_sequence)), data_sequence, where='post', linewidth=1.5)
    ax1.set_ylabel('Data Value', fontsize=12)
    ax1.set_title(title, fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Plot power trace
    ax2.plot(range(len(power_trace)), power_trace, linewidth=2, color='red')
    ax2.set_xlabel('Time (samples)', fontsize=12)
    ax2.set_ylabel('Power Consumption (AU)', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def demonstrate_simulation():
    """Demonstrate the Hamming weight power simulation."""
    print("=" * 60)
    print("Hamming Weight Power Simulation Demo")
    print("=" * 60)
    
    # Create traces folder
    traces_dir = Path("traces")
    traces_dir.mkdir(exist_ok=True)
    
    # Create simulator
    simulator = HammingPowerSimulator(bit_width=8, base_power=1.0, 
                                     transition_power=0.5, leakage_power=0.1)
    
    # Example 1: Specific sequence
    print("\n1. Simulating specific data sequence:")
    test_sequence = np.array([0x00, 0xFF, 0x00, 0xFF, 0xAA, 0x55, 0xF0, 0x0F])
    power_trace = simulator.simulate_sequence(test_sequence)
    
    print(f"   Data:  {[hex(x) for x in test_sequence]}")
    print(f"   Power: {power_trace.round(2)}")
    
    stats = simulator.analyze_power_statistics(power_trace)
    print("\n   Statistics:")
    for key, value in stats.items():
        print(f"   - {key}: {value:.3f}")
    
    # Example 2: Random sequence
    print("\n2. Simulating random data sequence:")
    data_seq, power_seq = simulator.simulate_random(num_samples=100, seed=None)
    
    stats = simulator.analyze_power_statistics(power_seq)
    print(f"   Generated {len(data_seq)} random samples")
    print("\n   Statistics:")
    for key, value in stats.items():
        print(f"   - {key}: {value:.3f}")
    
    # Example 3: Power analysis
    print("\n3. Analyzing correlation between Hamming weight and power:")
    hamming_weights = [simulator.hamming_weight(int(val)) for val in data_seq]
    correlation = np.corrcoef(hamming_weights, power_seq)[0, 1]
    print(f"   Correlation coefficient: {correlation:.3f}")
    
    # Generate plot
    print("\n4. Generating visualization...")
    plot_power_trace(data_seq[:50], power_seq[:50], 
                    "Hamming Weight Power Simulation (First 50 Samples)")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = traces_dir / f'power_trace_{timestamp}.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"   Plot saved to '{filename}'")
    
    print("\n" + "=" * 60)
    print("Simulation complete!")
    print("=" * 60)


if __name__ == "__main__":
    demonstrate_simulation()
