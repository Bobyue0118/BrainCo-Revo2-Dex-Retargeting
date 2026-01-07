#!/usr/bin/env python3
"""
Visualize the joint angle trajectory extracted from the video.
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import argparse


def plot_trajectory(trajectory_file: str, output_file: str = None):
    """
    Plot joint angle trajectories over time.
    
    Args:
        trajectory_file: Path to the JSON trajectory file
        output_file: Optional path to save the plot
    """
    # Load trajectory
    with open(trajectory_file, 'r') as f:
        trajectory = json.load(f)
    
    fps = trajectory['fps']
    frames = trajectory['frames']
    
    # Extract joint angles over time
    joint_names = None
    time_series = {}
    timestamps = []
    
    for frame_data in frames:
        if frame_data['joint_angles'] is not None:
            if joint_names is None:
                joint_names = sorted(frame_data['joint_angles'].keys())
                for joint_name in joint_names:
                    time_series[joint_name] = []
            
            timestamps.append(frame_data['timestamp'])
            for joint_name in joint_names:
                time_series[joint_name].append(frame_data['joint_angles'][joint_name])
    
    if not timestamps:
        print("No hand detected in the video!")
        return
    
    # Convert to numpy arrays
    timestamps = np.array(timestamps)
    
    # Group joints by finger
    finger_groups = {
        'Thumb': ['thumb_metacarpal_joint', 'thumb_proximal_joint', 'thumb_distal_joint'],
        'Index': ['index_proximal_joint', 'index_distal_joint'],
        'Middle': ['middle_proximal_joint', 'middle_distal_joint'],
        'Ring': ['ring_proximal_joint', 'ring_distal_joint'],
        'Pinky': ['pinky_proximal_joint', 'pinky_distal_joint']
    }
    
    # Create subplots
    fig, axes = plt.subplots(len(finger_groups), 1, figsize=(12, 10))
    fig.suptitle('Revo2 Hand Joint Angles Over Time', fontsize=16, fontweight='bold')
    
    colors = plt.cm.tab10(np.linspace(0, 1, 10))
    
    for idx, (finger_name, joint_list) in enumerate(finger_groups.items()):
        ax = axes[idx]
        
        color_idx = 0
        for joint_name in joint_names:
            # Check if this joint belongs to current finger
            if any(j in joint_name for j in joint_list):
                angles = np.array(time_series[joint_name])
                # Shorten joint name for legend
                short_name = joint_name.split('_')[-2] + '_' + joint_name.split('_')[-1]
                ax.plot(timestamps, angles, label=short_name, 
                       linewidth=2, color=colors[color_idx])
                color_idx += 1
        
        ax.set_ylabel('Angle (degrees)', fontsize=10)
        ax.set_xlabel('Time (seconds)', fontsize=10)
        ax.set_title(f'{finger_name} Finger', fontsize=12, fontweight='bold')
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {output_file}")
    
    plt.show()


def print_statistics(trajectory_file: str):
    """Print statistics about the trajectory."""
    with open(trajectory_file, 'r') as f:
        trajectory = json.load(f)
    
    frames = trajectory['frames']
    fps = trajectory['fps']
    
    detected_frames = sum(1 for f in frames if f['joint_angles'] is not None)
    total_frames = len(frames)
    
    print("\n" + "="*50)
    print("TRAJECTORY STATISTICS")
    print("="*50)
    print(f"Total frames: {total_frames}")
    print(f"Frames with hand detected: {detected_frames}")
    print(f"Detection rate: {detected_frames/total_frames*100:.1f}%")
    print(f"Video FPS: {fps}")
    print(f"Duration: {total_frames/fps:.2f} seconds")
    
    # Calculate joint angle statistics
    if detected_frames > 0:
        joint_stats = {}
        
        for frame_data in frames:
            if frame_data['joint_angles'] is not None:
                for joint_name, angle in frame_data['joint_angles'].items():
                    if joint_name not in joint_stats:
                        joint_stats[joint_name] = []
                    joint_stats[joint_name].append(angle)
        
        print("\nJoint Angle Ranges (degrees):")
        print("-" * 50)
        for joint_name in sorted(joint_stats.keys()):
            angles = np.array(joint_stats[joint_name])
            short_name = joint_name.split('_')[-2] + '_' + joint_name.split('_')[-1]
            print(f"{short_name:20s}: min={angles.min():6.2f}°, "
                  f"max={angles.max():6.2f}°, "
                  f"mean={angles.mean():6.2f}°, "
                  f"std={angles.std():6.2f}°")
    print("="*50 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Visualize hand retargeting trajectory')
    parser.add_argument('--trajectory', type=str, required=True,
                       help='Path to trajectory JSON file')
    parser.add_argument('--output', type=str, default=None,
                       help='Path to save the plot image')
    parser.add_argument('--stats-only', action='store_true',
                       help='Only print statistics without plotting')
    
    args = parser.parse_args()
    
    # Print statistics
    print_statistics(args.trajectory)
    
    # Plot trajectory
    if not args.stats_only:
        plot_trajectory(args.trajectory, args.output)


if __name__ == '__main__':
    main()
