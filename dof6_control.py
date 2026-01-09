#!/usr/bin/env python3
"""
6-DOF Hand Control Demonstration
Shows how to use the controllable 6-DOF trajectory for actual robot control.
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List
import argparse


def load_6dof_trajectory(filepath: str) -> Dict:
    """
    Load 6-DOF controllable trajectory from JSON file.
    
    Args:
        filepath: Path to 6-DOF trajectory JSON file
        
    Returns:
        Trajectory dictionary with controllable joints only
    """
    with open(filepath, 'r') as f:
        trajectory = json.load(f)
    
    print(f"✓ Loaded 6-DOF trajectory from: {filepath}")
    print(f"  DOF: {trajectory['dof']}")
    print(f"  Frames: {len(trajectory['frames'])}")
    print(f"  FPS: {trajectory['fps']}")
    print(f"  Angle unit: {trajectory.get('angle_unit', 'radians')}")
    print(f"\n📋 Controllable Joints:")
    for i, (short_name, full_name) in enumerate(zip(trajectory['joints'], trajectory['joint_names']), 1):
        print(f"  {i}. {short_name:20} → {full_name}")
    
    if trajectory.get('mimic_info'):
        print(f"\n🔗 Mimic Joints (automatically controlled):")
        for joint_name, info in trajectory['mimic_info'].items():
            parent = info['parent']
            mult = info['multiplier']
            offset = info['offset']
            print(f"  {joint_name}")
            print(f"    └─ mimics: {parent}")
            print(f"       formula: angle = {mult} * parent_angle + {offset}")
    
    return trajectory


def export_to_control_format(trajectory: Dict, output_format: str = 'csv'):
    """
    Export 6-DOF trajectory to robot control format.
    
    Args:
        trajectory: 6-DOF trajectory data
        output_format: Output format ('csv', 'numpy', or 'text')
    """
    frames = trajectory['frames']
    joint_names = trajectory['joint_names']
    
    if output_format == 'csv':
        # Export to CSV
        output_path = 'control_trajectory_6dof.csv'
        with open(output_path, 'w') as f:
            # Header
            f.write('frame,' + ','.join(joint_names) + '\n')
            
            # Data
            for frame_idx, frame in enumerate(frames):
                values = [str(frame.get(joint, 0.0)) for joint in joint_names]
                f.write(f"{frame_idx}," + ','.join(values) + '\n')
        
        print(f"\n✓ Exported to CSV: {output_path}")
    
    elif output_format == 'numpy':
        # Export to numpy array
        output_path = 'control_trajectory_6dof.npy'
        
        # Create matrix: [num_frames x 6_joints]
        data_matrix = []
        for frame in frames:
            row = [frame.get(joint, 0.0) for joint in joint_names]
            data_matrix.append(row)
        
        np.save(output_path, np.array(data_matrix))
        print(f"\n✓ Exported to NumPy: {output_path}")
        print(f"  Shape: {np.array(data_matrix).shape} (frames x joints)")
    
    elif output_format == 'text':
        # Export to human-readable text
        output_path = 'control_trajectory_6dof.txt'
        with open(output_path, 'w') as f:
            f.write("BrainCo Hand 6-DOF Control Trajectory\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Total Frames: {len(frames)}\n")
            f.write(f"FPS: {trajectory['fps']}\n")
            f.write(f"Duration: {len(frames) / trajectory['fps']:.2f} seconds\n\n")
            f.write("Controllable Joints (6 DOF):\n")
            for i, (short_name, full_name) in enumerate(zip(trajectory['joints'], joint_names), 1):
                f.write(f"  {i}. {full_name}\n")
            f.write("\n" + "=" * 60 + "\n\n")
            
            # Write trajectory data
            for frame_idx, frame in enumerate(frames[:10]):  # First 10 frames as example
                f.write(f"Frame {frame_idx}:\n")
                for joint in joint_names:
                    angle = frame.get(joint, 0.0)
                    f.write(f"  {joint:40} = {angle:8.4f} rad ({np.degrees(angle):7.2f}°)\n")
                f.write("\n")
            
            if len(frames) > 10:
                f.write(f"... ({len(frames) - 10} more frames)\n")
        
        print(f"\n✓ Exported to text: {output_path}")


def get_frame_command(trajectory: Dict, frame_idx: int) -> Dict[str, float]:
    """
    Get control command for a specific frame.
    
    Args:
        trajectory: 6-DOF trajectory data
        frame_idx: Frame index to retrieve
        
    Returns:
        Dictionary of joint names to angles (radians)
    """
    if frame_idx < 0 or frame_idx >= len(trajectory['frames']):
        raise ValueError(f"Frame index {frame_idx} out of range [0, {len(trajectory['frames'])-1}]")
    
    return trajectory['frames'][frame_idx]


def compute_mimic_joint_angles(controllable_angles: Dict[str, float], 
                               mimic_info: Dict[str, Dict]) -> Dict[str, float]:
    """
    Compute angles for mimic joints based on controllable joints.
    
    Args:
        controllable_angles: Dictionary of controllable joint angles
        mimic_info: Mimic joint information from trajectory
        
    Returns:
        Dictionary of all joint angles (controllable + mimic)
    """
    all_angles = controllable_angles.copy()
    
    for joint_name, info in mimic_info.items():
        parent_joint = info['parent']
        multiplier = info['multiplier']
        offset = info['offset']
        
        if parent_joint in all_angles:
            # Calculate mimic joint angle
            all_angles[joint_name] = multiplier * all_angles[parent_joint] + offset
    
    return all_angles


def analyze_trajectory_stats(trajectory: Dict):
    """Analyze and print statistics about the 6-DOF trajectory."""
    frames = trajectory['frames']
    joint_names = trajectory['joint_names']
    angle_unit = trajectory.get('angle_unit', 'radians')
    
    print(f"\n📊 Trajectory Statistics:")
    print(f"{'='*60}")
    
    for joint_name in joint_names:
        angles = [frame.get(joint_name, 0.0) for frame in frames]
        
        min_angle = np.min(angles)
        max_angle = np.max(angles)
        mean_angle = np.mean(angles)
        std_angle = np.std(angles)
        
        print(f"\n{joint_name}:")
        if angle_unit == 'degrees':
            print(f"  Range: [{min_angle:6.2f}°, {max_angle:6.2f}°]")
            print(f"         [{np.radians(min_angle):6.4f}, {np.radians(max_angle):6.4f}] rad")
            print(f"  Mean:  {mean_angle:6.2f}° ({np.radians(mean_angle):6.4f} rad)")
            print(f"  Std:   {std_angle:6.2f}° ({np.radians(std_angle):6.4f} rad)")
        else:
            print(f"  Range: [{min_angle:6.3f}, {max_angle:6.3f}] rad")
            print(f"         [{np.degrees(min_angle):6.2f}°, {np.degrees(max_angle):6.2f}°]")
            print(f"  Mean:  {mean_angle:6.3f} rad ({np.degrees(mean_angle):6.2f}°)")
            print(f"  Std:   {std_angle:6.3f} rad ({np.degrees(std_angle):6.2f}°)")


def main():
    parser = argparse.ArgumentParser(
        description="6-DOF Hand Control Demonstration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Load and inspect 6-DOF trajectory
  python dof6_control.py --trajectory hand_trajectory_6dof.json
  
  # Export to CSV for robot control
  python dof6_control.py --trajectory hand_trajectory_6dof.json --export csv
  
  # Export to NumPy array
  python dof6_control.py --trajectory hand_trajectory_6dof.json --export numpy
  
  # Show statistics
  python dof6_control.py --trajectory hand_trajectory_6dof.json --stats
        """
    )
    
    parser.add_argument('--trajectory', type=str, default='hand_trajectory_6dof.json',
                       help='Path to 6-DOF trajectory JSON file')
    parser.add_argument('--export', type=str, choices=['csv', 'numpy', 'text'],
                       help='Export trajectory to specified format')
    parser.add_argument('--stats', action='store_true',
                       help='Show trajectory statistics')
    parser.add_argument('--frame', type=int,
                       help='Show command for specific frame')
    
    args = parser.parse_args()
    
    # Check if file exists
    if not Path(args.trajectory).exists():
        print(f"✗ Error: Trajectory file not found: {args.trajectory}")
        print("\nRun hand retargeting first to generate the 6-DOF trajectory:")
        print("  python hand_retargeting.py --video <video> --urdf <urdf> --hand right")
        return 1
    
    print("\n" + "="*60)
    print("6-DOF Hand Control Demonstration")
    print("="*60 + "\n")
    
    # Load trajectory
    trajectory = load_6dof_trajectory(args.trajectory)
    
    # Export if requested
    if args.export:
        export_to_control_format(trajectory, args.export)
    
    # Show statistics if requested
    if args.stats:
        analyze_trajectory_stats(trajectory)
    
    # Show specific frame if requested
    if args.frame is not None:
        print(f"\n🎯 Frame {args.frame} Control Command:")
        print("="*60)
        try:
            command = get_frame_command(trajectory, args.frame)
            angle_unit = trajectory.get('angle_unit', 'radians')
            
            print("\nControllable Joints (send to robot):")
            for joint_name, angle in command.items():
                if angle_unit == 'degrees':
                    print(f"  {joint_name:40} = {angle:8.4f}° ({np.radians(angle):7.4f} rad)")
                else:
                    print(f"  {joint_name:40} = {angle:8.4f} rad ({np.degrees(angle):7.2f}°)")
            
            # Show mimic joint calculations
            if trajectory.get('mimic_info'):
                all_angles = compute_mimic_joint_angles(command, trajectory['mimic_info'])
                print("\nMimic Joints (automatically calculated):")
                for joint_name in trajectory['mimic_info'].keys():
                    if joint_name in all_angles:
                        angle = all_angles[joint_name]
                        if angle_unit == 'degrees':
                            print(f"  {joint_name:40} = {angle:8.4f}° ({np.radians(angle):7.4f} rad)")
                        else:
                            print(f"  {joint_name:40} = {angle:8.4f} rad ({np.degrees(angle):7.2f}°)")
        except ValueError as e:
            print(f"\n✗ Error: {e}")
            return 1
    
    print("\n" + "="*60)
    print("✓ Complete!")
    print("="*60)
    
    if not args.export and not args.stats and args.frame is None:
        print("\n💡 Try:")
        print(f"  --export csv    # Export to CSV for robot control")
        print(f"  --stats         # Show trajectory statistics")
        print(f"  --frame 0       # Show control command for frame 0")
    
    return 0


if __name__ == "__main__":
    exit(main())
