#!/usr/bin/env python3
"""
Example script demonstrating advanced usage of the hand retargeting system.
"""

import json
import numpy as np
from pathlib import Path
from hand_retargeting import Revo2HandRetargeting


def example_basic_usage():
    """Basic example: Process a video and save results."""
    print("="*60)
    print("EXAMPLE 1: Basic Video Processing")
    print("="*60)
    
    # Initialize retargeting system
    retargeting = Revo2HandRetargeting(
        urdf_path="Revo2_URDF Description_ROS2/revo2_description/urdf/revo2_right_hand.urdf",
        hand_side="right"
    )
    
    # Process video
    trajectory = retargeting.process_video(
        video_path="human_hand_video.mp4",
        output_path="output_annotated.mp4",
        save_trajectory=True
    )
    
    print("\nDone! Check output_annotated.mp4 and hand_trajectory.json")


def example_analyze_trajectory():
    """Example: Analyze a saved trajectory."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Trajectory Analysis")
    print("="*60)
    
    trajectory_file = "hand_trajectory.json"
    
    if not Path(trajectory_file).exists():
        print(f"Error: {trajectory_file} not found. Run example 1 first.")
        return
    
    # Load trajectory
    with open(trajectory_file, 'r') as f:
        trajectory = json.load(f)
    
    fps = trajectory['fps']
    frames = trajectory['frames']
    
    # Find frames with maximum finger flexion
    max_flexion = {}
    
    for frame_data in frames:
        if frame_data['joint_angles'] is None:
            continue
        
        for joint_name, angle in frame_data['joint_angles'].items():
            if joint_name not in max_flexion or angle > max_flexion[joint_name]['angle']:
                max_flexion[joint_name] = {
                    'angle': angle,
                    'frame': frame_data['frame'],
                    'timestamp': frame_data['timestamp']
                }
    
    print("\nMaximum Joint Angles Detected:")
    print("-" * 60)
    for joint_name, data in sorted(max_flexion.items()):
        print(f"{joint_name:30s}: {data['angle']:6.2f}° at t={data['timestamp']:.2f}s")


def example_export_to_csv():
    """Example: Export trajectory to CSV for external analysis."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Export to CSV")
    print("="*60)
    
    trajectory_file = "hand_trajectory.json"
    
    if not Path(trajectory_file).exists():
        print(f"Error: {trajectory_file} not found. Run example 1 first.")
        return
    
    with open(trajectory_file, 'r') as f:
        trajectory = json.load(f)
    
    # Prepare CSV data
    csv_lines = []
    
    # Get all joint names
    joint_names = None
    for frame_data in trajectory['frames']:
        if frame_data['joint_angles'] is not None:
            joint_names = sorted(frame_data['joint_angles'].keys())
            break
    
    if joint_names is None:
        print("No hand detected in trajectory!")
        return
    
    # Header
    header = "frame,timestamp," + ",".join(joint_names)
    csv_lines.append(header)
    
    # Data rows
    for frame_data in trajectory['frames']:
        if frame_data['joint_angles'] is not None:
            row = f"{frame_data['frame']},{frame_data['timestamp']:.4f}"
            for joint_name in joint_names:
                angle = frame_data['joint_angles'][joint_name]
                row += f",{angle:.4f}"
            csv_lines.append(row)
    
    # Write to file
    csv_file = "hand_trajectory.csv"
    with open(csv_file, 'w') as f:
        f.write("\n".join(csv_lines))
    
    print(f"\nTrajectory exported to: {csv_file}")
    print(f"Total data points: {len(csv_lines) - 1}")


def example_custom_mapping():
    """Example: Custom joint angle mapping with scaling."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Custom Joint Mapping")
    print("="*60)
    
    trajectory_file = "hand_trajectory.json"
    
    if not Path(trajectory_file).exists():
        print(f"Error: {trajectory_file} not found. Run example 1 first.")
        return
    
    with open(trajectory_file, 'r') as f:
        trajectory = json.load(f)
    
    # Apply custom scaling factors (e.g., reduce finger flexion by 20%)
    scaling_factors = {
        'index': 0.8,
        'middle': 0.8,
        'ring': 0.8,
        'pinky': 0.8,
        'thumb': 1.0  # No scaling for thumb
    }
    
    scaled_trajectory = trajectory.copy()
    
    for frame_data in scaled_trajectory['frames']:
        if frame_data['joint_angles'] is not None:
            scaled_angles = {}
            for joint_name, angle in frame_data['joint_angles'].items():
                # Determine which finger
                for finger, scale in scaling_factors.items():
                    if finger in joint_name:
                        scaled_angles[joint_name] = angle * scale
                        break
                else:
                    scaled_angles[joint_name] = angle
            
            frame_data['joint_angles'] = scaled_angles
    
    # Save scaled trajectory
    output_file = "hand_trajectory_scaled.json"
    with open(output_file, 'w') as f:
        json.dump(scaled_trajectory, f, indent=2)
    
    print(f"\nScaled trajectory saved to: {output_file}")
    print("Scaling factors applied:")
    for finger, scale in scaling_factors.items():
        print(f"  {finger}: {scale*100:.0f}%")


def example_motion_statistics():
    """Example: Calculate motion statistics."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Motion Statistics")
    print("="*60)
    
    trajectory_file = "hand_trajectory.json"
    
    if not Path(trajectory_file).exists():
        print(f"Error: {trajectory_file} not found. Run example 1 first.")
        return
    
    with open(trajectory_file, 'r') as f:
        trajectory = json.load(f)
    
    # Calculate velocities (angular velocity in deg/s)
    fps = trajectory['fps']
    dt = 1.0 / fps
    
    velocities = {}
    
    prev_angles = None
    for frame_data in trajectory['frames']:
        if frame_data['joint_angles'] is not None:
            if prev_angles is not None:
                for joint_name, angle in frame_data['joint_angles'].items():
                    if joint_name in prev_angles:
                        velocity = (angle - prev_angles[joint_name]) / dt
                        if joint_name not in velocities:
                            velocities[joint_name] = []
                        velocities[joint_name].append(abs(velocity))
            
            prev_angles = frame_data['joint_angles'].copy()
    
    print("\nJoint Motion Statistics:")
    print("-" * 60)
    print(f"{'Joint Name':<30s} {'Avg Vel':<12s} {'Max Vel':<12s}")
    print("-" * 60)
    
    for joint_name in sorted(velocities.keys()):
        vels = np.array(velocities[joint_name])
        avg_vel = np.mean(vels)
        max_vel = np.max(vels)
        print(f"{joint_name:<30s} {avg_vel:8.2f} °/s  {max_vel:8.2f} °/s")


def main():
    """Run all examples."""
    import sys
    
    if len(sys.argv) > 1:
        example_num = int(sys.argv[1])
        examples = {
            1: example_basic_usage,
            2: example_analyze_trajectory,
            3: example_export_to_csv,
            4: example_custom_mapping,
            5: example_motion_statistics
        }
        
        if example_num in examples:
            examples[example_num]()
        else:
            print(f"Example {example_num} not found!")
    else:
        print("Hand Retargeting Examples")
        print("=" * 60)
        print("\nAvailable examples:")
        print("  1. Basic video processing")
        print("  2. Trajectory analysis")
        print("  3. Export to CSV")
        print("  4. Custom joint mapping")
        print("  5. Motion statistics")
        print("\nUsage: python examples.py <example_number>")
        print("   or: python examples.py       (run all)")
        print()
        
        # Run all examples in sequence
        response = input("Run all examples? (y/n): ")
        if response.lower() == 'y':
            example_basic_usage()
            example_analyze_trajectory()
            example_export_to_csv()
            example_custom_mapping()
            example_motion_statistics()
            
            print("\n" + "="*60)
            print("All examples completed!")
            print("="*60)


if __name__ == '__main__':
    main()
