#!/usr/bin/env python3
"""
Plot 6-DOF hand trajectory from JSON file.
Visualizes joint angles over time with proper handling of missing frames.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import argparse


def load_trajectory(json_path: str) -> dict:
    """Load trajectory data from JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)


def plot_trajectory(trajectory_data: dict, output_path: str = None, show: bool = True):
    """
    Plot 6-DOF joint trajectory with separate subplots for each joint.
    
    Args:
        trajectory_data: Dictionary containing trajectory data
        output_path: Path to save the plot (optional)
        show: Whether to display the plot
    """
    fps = trajectory_data['fps']
    joint_names = trajectory_data['joint_names']
    frames = trajectory_data['frames']
    
    # Prepare data arrays
    num_frames = len(frames)
    time = np.arange(num_frames) / fps  # Time in seconds
    
    # Extract joint angles for each joint (handle missing frames)
    joint_data = {jname: [] for jname in joint_names}
    valid_indices = []
    
    for idx, frame in enumerate(frames):
        if frame and isinstance(frame, dict) and len(frame) > 0:
            valid_indices.append(idx)
            for jname in joint_names:
                joint_data[jname].append(frame.get(jname, np.nan))
        else:
            for jname in joint_names:
                joint_data[jname].append(np.nan)
    
    # Convert to numpy arrays
    for jname in joint_names:
        joint_data[jname] = np.array(joint_data[jname])
    
    # Create figure with subplots
    fig, axes = plt.subplots(3, 2, figsize=(14, 10))
    fig.suptitle('6-DOF Hand Joint Trajectory', fontsize=16, fontweight='bold')
    
    # Flatten axes for easier iteration
    axes = axes.flatten()
    
    # Color map for different joints
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    # Plot each joint
    for idx, (jname, ax, color) in enumerate(zip(joint_names, axes, colors)):
        angles = joint_data[jname]
        
        # Plot line (will handle NaN automatically)
        ax.plot(time, angles, linewidth=2, color=color, label=jname.replace('right_', '').replace('_joint', ''))
        
        # Mark valid data points
        valid_time = time[~np.isnan(angles)]
        valid_angles = angles[~np.isnan(angles)]
        ax.scatter(valid_time, valid_angles, s=20, color=color, alpha=0.6, zorder=3)
        
        # Formatting
        ax.set_xlabel('Time (s)', fontsize=10)
        ax.set_ylabel('Angle (degrees)', fontsize=10)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(loc='upper right', fontsize=9)
        
        # Set y-axis limits with some padding
        if len(valid_angles) > 0:
            y_min, y_max = np.min(valid_angles), np.max(valid_angles)
            y_range = y_max - y_min
            if y_range > 0:
                ax.set_ylim(y_min - 0.1 * y_range, y_max + 0.1 * y_range)
            else:
                ax.set_ylim(y_min - 5, y_max + 5)
        
        # Add horizontal line at 0
        ax.axhline(y=0, color='gray', linestyle=':', linewidth=1, alpha=0.5)
    
    # Add metadata text
    metadata_text = (
        f"FPS: {fps}\n"
        f"Total Frames: {num_frames}\n"
        f"Valid Frames: {len(valid_indices)}\n"
        f"Duration: {num_frames/fps:.2f}s\n"
        f"Coverage: {len(valid_indices)/num_frames*100:.1f}%"
    )
    fig.text(0.02, 0.02, metadata_text, fontsize=9, family='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    
    # Save plot
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {output_path}")
    
    # Show plot
    if show:
        plt.show()
    
    plt.close()


def plot_combined_trajectory(trajectory_data: dict, output_path: str = None, show: bool = True):
    """
    Plot all 6 joints in a single plot for comparison.
    
    Args:
        trajectory_data: Dictionary containing trajectory data
        output_path: Path to save the plot (optional)
        show: Whether to display the plot
    """
    fps = trajectory_data['fps']
    joint_names = trajectory_data['joint_names']
    frames = trajectory_data['frames']
    
    num_frames = len(frames)
    time = np.arange(num_frames) / fps
    
    # Extract joint angles
    joint_data = {jname: [] for jname in joint_names}
    for frame in frames:
        if frame and isinstance(frame, dict) and len(frame) > 0:
            for jname in joint_names:
                joint_data[jname].append(frame.get(jname, np.nan))
        else:
            for jname in joint_names:
                joint_data[jname].append(np.nan)
    
    # Convert to numpy arrays
    for jname in joint_names:
        joint_data[jname] = np.array(joint_data[jname])
    
    # Create figure
    plt.figure(figsize=(14, 8))
    
    # Color map
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    # Plot all joints
    for jname, color in zip(joint_names, colors):
        angles = joint_data[jname]
        label = jname.replace('right_', '').replace('_joint', '')
        plt.plot(time, angles, linewidth=2, color=color, label=label, alpha=0.8)
    
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('Joint Angle (degrees)', fontsize=12)
    plt.title('6-DOF Hand Joint Trajectory - Combined View', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(loc='best', fontsize=10, ncol=2)
    plt.axhline(y=0, color='gray', linestyle=':', linewidth=1, alpha=0.5)
    
    plt.tight_layout()
    
    if output_path:
        combined_path = output_path.replace('.png', '_combined.png')
        plt.savefig(combined_path, dpi=300, bbox_inches='tight')
        print(f"Combined plot saved to: {combined_path}")
    
    if show:
        plt.show()
    
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Plot 6-DOF hand trajectory from JSON file')
    parser.add_argument('--input', type=str, required=True,
                       help='Path to hand_trajectory_6dof.json file')
    parser.add_argument('--output', type=str, default=None,
                       help='Path to save output plot (default: same directory as input)')
    parser.add_argument('--combined', action='store_true',
                       help='Also generate combined plot with all joints')
    parser.add_argument('--no-show', action='store_true',
                       help='Do not display the plot')
    
    args = parser.parse_args()
    
    # Load trajectory
    trajectory = load_trajectory(args.input)
    
    # Determine output path
    if args.output is None:
        input_path = Path(args.input)
        output_path = str(input_path.parent / 'trajectory_6dof_plot.png')
    else:
        output_path = args.output
    
    print(f"Plotting trajectory from: {args.input}")
    
    # Plot separate subplots
    plot_trajectory(trajectory, output_path=output_path, show=not args.no_show)
    
    # Plot combined view if requested
    if args.combined:
        plot_combined_trajectory(trajectory, output_path=output_path, show=not args.no_show)
    
    print("Done!")


if __name__ == '__main__':
    main()