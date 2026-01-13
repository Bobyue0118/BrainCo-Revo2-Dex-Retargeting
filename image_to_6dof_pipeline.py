#!/usr/bin/env python3
"""
Complete Image-to-6DOF Pipeline
Input: Image folder
Output: 6-DOF control commands + rendered hand poses

This script provides an end-to-end pipeline:
1. Process images to detect hand and extract joint angles
2. Generate 6-DOF controllable trajectory
3. Render robotic hand poses showing the retargeted configuration
4. Export control commands in various formats
"""

import argparse
import sys
from pathlib import Path
import json
import subprocess
import shutil
from datetime import datetime
import numpy as np


# Motor control normalization parameters
# Maximum joint angles in degrees for each joint (supports both left and right hands)
JOINT_MAX_ANGLES = {
    # Right hand joints
    'right_thumb_metacarpal_joint': 90,
    'right_thumb_proximal_joint': 59,
    'right_index_proximal_joint': 81,
    'right_middle_proximal_joint': 81,
    'right_ring_proximal_joint': 81,
    'right_pinky_proximal_joint': 81,
    # Left hand joints (same max angles as right hand)
    'left_thumb_metacarpal_joint': 90,
    'left_thumb_proximal_joint': 59,
    'left_index_proximal_joint': 81,
    'left_middle_proximal_joint': 81,
    'left_ring_proximal_joint': 81,
    'left_pinky_proximal_joint': 81
}

# Motor command range
MOTOR_MIN = 0
MOTOR_MAX = 1000


def generate_motor_commands(trajectory_6dof_path: str, output_path: str):
    """
    Generate motor control commands from 6-DOF trajectory.
    
    Process:
    1. Normalize each joint angle by its maximum angle
    2. Remap normalized values to motor range [0, 1000]
    
    Args:
        trajectory_6dof_path: Path to 6-DOF trajectory JSON
        output_path: Path to save motor commands CSV
    """
    # Load 6-DOF trajectory
    with open(trajectory_6dof_path, 'r') as f:
        trajectory = json.load(f)
    
    frames = trajectory['frames']
    
    # Auto-detect joint names from the trajectory data
    # Get joint names from the first valid frame or from trajectory metadata
    joint_names = None
    if 'joint_names' in trajectory:
        joint_names = trajectory['joint_names']
    else:
        # Detect from first valid frame
        for frame_data in frames:
            if frame_data is not None and isinstance(frame_data, dict):
                if 'joint_angles' in frame_data and frame_data['joint_angles'] is not None:
                    joint_names = [j for j in frame_data['joint_angles'].keys() if j in JOINT_MAX_ANGLES]
                    break
                else:
                    # Flat structure
                    joint_names = [j for j in frame_data.keys() if j in JOINT_MAX_ANGLES]
                    break
    
    if not joint_names:
        raise ValueError("Could not detect joint names from trajectory")
    
    # Generate motor commands
    motor_commands = []
    
    for frame_data in frames:
        # 6-DOF trajectory frames are flat dictionaries with joint angles directly
        # Check if frame_data is None or empty
        if frame_data is None:
            motor_commands.append(None)
            continue
        
        # Get joint angles - handle both flat and nested structure
        if isinstance(frame_data, dict):
            if 'joint_angles' in frame_data:
                joint_angles = frame_data['joint_angles']
                if joint_angles is None:
                    motor_commands.append(None)
                    continue
            else:
                # Flat structure - frame_data IS the joint angles
                joint_angles = frame_data
        else:
            motor_commands.append(None)
            continue
        
        frame_motor = {}
        for joint_name in joint_names:
            if joint_name in joint_angles and joint_name in JOINT_MAX_ANGLES:
                angle = joint_angles[joint_name]
                max_angle = JOINT_MAX_ANGLES[joint_name]
                
                # Normalize by max angle (clamp to [0, 1])
                normalized = np.clip(angle / max_angle, 0, 1)
                
                # Remap to motor range [0, 1000]
                motor_value = int(normalized * (MOTOR_MAX - MOTOR_MIN) + MOTOR_MIN)
                frame_motor[joint_name] = motor_value
        
        motor_commands.append(frame_motor)
    
    # Save to CSV
    with open(output_path, 'w') as f:
        # Header
        f.write('frame,' + ','.join(joint_names) + '\n')
        
        # Data
        for idx, motor_cmd in enumerate(motor_commands):
            if motor_cmd is None:
                # Write empty values for skipped frames
                f.write(f'{idx},' + ','.join([''] * len(joint_names)) + '\n')
            else:
                values = [str(motor_cmd.get(j, 0)) for j in joint_names]
                f.write(f'{idx},' + ','.join(values) + '\n')
    
    # Also save as JSON for easier programmatic access
    json_output_path = output_path.replace('.csv', '.json')
    motor_trajectory = {
        'description': 'Motor control commands normalized and remapped to [0, 1000]',
        'normalization': {j: f'angle / {JOINT_MAX_ANGLES[j]}' for j in joint_names if j in JOINT_MAX_ANGLES},
        'motor_range': [MOTOR_MIN, MOTOR_MAX],
        'joint_max_angles': {j: JOINT_MAX_ANGLES[j] for j in joint_names if j in JOINT_MAX_ANGLES},
        'frames': motor_commands
    }
    
    with open(json_output_path, 'w') as f:
        json.dump(motor_trajectory, f, indent=2)
    
    return len([m for m in motor_commands if m is not None])


def print_header(title: str):
    """Print formatted header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def run_command(cmd: list, description: str):
    """Run a command and handle errors."""
    print(f"▶ {description}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"✗ Error: {description} failed")
        print(result.stderr)
        sys.exit(1)
    
    print(f"✓ {description} complete")
    return result


def main():
    parser = argparse.ArgumentParser(
        description='Complete Image-to-6DOF Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Complete pipeline from images to robot control:

1. Detect hands in images and extract joint angles
2. Generate 6-DOF controllable trajectory  
3. Render retargeted robotic hand poses
4. Export control commands (CSV/NumPy)

Examples:
  # Basic usage
  python image_to_6dof_pipeline.py \\
      --input image_frames/ \\
      --urdf brainco_hand/brainco_right.urdf \\
      --output results/
  
  # With custom settings
  python image_to_6dof_pipeline.py \\
      --input frames/ \\
      --urdf brainco_hand/brainco_right.urdf \\
      --output results/ \\
      --pattern "*.png" \\
      --fps 30 \\
      --export csv \\
      --render-width 1280 \\
      --render-height 720
        """
    )
    
    # Required arguments
    parser.add_argument('--input', type=str, required=True,
                       help='Input image folder')
    parser.add_argument('--urdf', type=str, required=False,
                       help='Path to URDF file (auto-selected based on --hand if not specified)')
    parser.add_argument('--output', type=str, required=True,
                       help='Output folder for all results')
    
    # Optional arguments
    parser.add_argument('--hand', type=str, default='right', choices=['right', 'left'],
                       help='Hand side (default: right)')
    parser.add_argument('--pattern', type=str, default='*.jpg',
                       help='Image file pattern (default: *.jpg)')
    parser.add_argument('--fps', type=float, default=30.0,
                       help='Frame rate for trajectory (default: 30)')
    parser.add_argument('--export', type=str, choices=['csv', 'numpy', 'text', 'all'],
                       default='csv',
                       help='Export format for control commands (default: csv)')
    parser.add_argument('--render-width', type=int, default=640,
                       help='Width of rendered hand images (default: 640)')
    parser.add_argument('--render-height', type=int, default=480,
                       help='Height of rendered hand images (default: 480)')
    parser.add_argument('--skip-render', action='store_true',
                       help='Skip rendering hand poses (faster)')
    parser.add_argument('--skip-export', action='store_true',
                       help='Skip exporting control commands')
    parser.add_argument('--no-timestamp', action='store_true',
                       help='Disable timestamp directory (will overwrite existing results)')
    
    args = parser.parse_args()
    
    # Validate paths
    input_folder = Path(args.input)
    if not input_folder.exists():
        print(f"✗ Error: Input folder not found: {input_folder}")
        sys.exit(1)
    
    # Auto-select URDF if not specified
    if args.urdf is None:
        urdf_path = Path(f"brainco_hand/brainco_{args.hand}.urdf")
        if not urdf_path.exists():
            print(f"✗ Error: Auto-selected URDF not found: {urdf_path}")
            print(f"  Please specify URDF with --urdf option")
            sys.exit(1)
        args.urdf = str(urdf_path)
        print(f"ℹ Auto-selected URDF: {args.urdf}")
    
    if not Path(args.urdf).exists():
        print(f"✗ Error: URDF file not found: {args.urdf}")
        sys.exit(1)
    
    # Create output structure with optional timestamp
    output_root = Path(args.output)
    
    # Add timestamp directory unless disabled
    if not args.no_timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        timestamped_output = output_root / timestamp
        use_timestamp = True
    else:
        timestamped_output = output_root
        timestamp = None
        use_timestamp = False
    
    timestamped_output.mkdir(parents=True, exist_ok=True)
    
    annotated_folder = timestamped_output / "annotated_images"
    rendered_folder = timestamped_output / "rendered_hand_poses"
    trajectories_folder = timestamped_output / "trajectories"
    control_folder = timestamped_output / "control_commands"
    
    annotated_folder.mkdir(exist_ok=True)
    rendered_folder.mkdir(exist_ok=True)
    trajectories_folder.mkdir(exist_ok=True)
    control_folder.mkdir(exist_ok=True)
    
    # Validate URDF matches hand side and auto-correct if mismatched
    urdf_filename = Path(args.urdf).name.lower()
    correct_urdf = Path(f"brainco_hand/brainco_{args.hand}.urdf")
    
    if 'left' in urdf_filename and args.hand == 'right':
        print(f"\n⚠ WARNING: Using LEFT hand URDF ({args.urdf}) but detecting RIGHT hand!")
        print(f"  Auto-correcting to: {correct_urdf}")
        if correct_urdf.exists():
            args.urdf = str(correct_urdf)
            print(f"  ✓ Switched to correct URDF for right hand")
        else:
            print(f"  ✗ Error: Correct URDF not found: {correct_urdf}")
            response = input("\nContinue with mismatched URDF anyway? (y/N): ")
            if response.lower() != 'y':
                print("Aborted.")
                sys.exit(0)
    elif 'right' in urdf_filename and args.hand == 'left':
        print(f"\n⚠ WARNING: Using RIGHT hand URDF ({args.urdf}) but detecting LEFT hand!")
        print(f"  Auto-correcting to: {correct_urdf}")
        if correct_urdf.exists():
            args.urdf = str(correct_urdf)
            print(f"  ✓ Switched to correct URDF for left hand")
        else:
            print(f"  ✗ Error: Correct URDF not found: {correct_urdf}")
            response = input("\nContinue with mismatched URDF anyway? (y/N): ")
            if response.lower() != 'y':
                print("Aborted.")
                sys.exit(0)
    
    print_header("Image-to-6DOF Pipeline")
    print(f"Input:     {input_folder}")
    print(f"URDF:      {args.urdf}")
    print(f"Output:    {output_root}")
    if use_timestamp:
        print(f"Timestamp: {timestamp}")
        print(f"Session:   {timestamped_output}")
    print(f"Hand:      {args.hand}")
    print(f"FPS:       {args.fps}")
    
    # =================================================================
    # STEP 1: Process images to extract hand joint angles
    # =================================================================
    print_header("STEP 1: Hand Detection & Retargeting")
    
    cmd = [
        'python', 'image_retargeting.py',
        '--folder', str(input_folder),
        '--urdf', args.urdf,
        '--hand', args.hand,
        '--pattern', args.pattern,
        '--fps', str(args.fps),
        '--output', str(annotated_folder)
    ]
    
    run_command(cmd, "Processing images")
    
    # Move generated trajectories to output folder
    traj_11dof = input_folder / 'hand_trajectory.json'
    traj_6dof = input_folder / 'hand_trajectory_6dof.json'
    
    if traj_11dof.exists():
        shutil.move(str(traj_11dof), str(trajectories_folder / 'hand_trajectory.json'))
        print(f"  → Saved 11-DOF trajectory to: {trajectories_folder / 'hand_trajectory.json'}")
    
    if traj_6dof.exists():
        shutil.move(str(traj_6dof), str(trajectories_folder / 'hand_trajectory_6dof.json'))
        print(f"  → Saved 6-DOF trajectory to: {trajectories_folder / 'hand_trajectory_6dof.json'}")
    
    # Load trajectory to get statistics
    traj_path = trajectories_folder / 'hand_trajectory.json'
    with open(traj_path, 'r') as f:
        trajectory = json.load(f)
    
    total_frames = len(trajectory['frames'])
    detected_frames = sum(1 for f in trajectory['frames'] if f['joint_angles'] is not None)
    
    print(f"\n  Statistics:")
    print(f"    Total frames: {total_frames}")
    print(f"    Detected: {detected_frames}/{total_frames} ({100*detected_frames/total_frames:.1f}%)")
    
    # =================================================================
    # STEP 2: Render retargeted hand poses
    # =================================================================
    if not args.skip_render:
        print_header("STEP 2: Rendering Robotic Hand Poses")
        
        cmd = [
            'python', 'render_hand_poses.py',
            '--trajectory', str(trajectories_folder / 'hand_trajectory.json'),
            '--urdf', args.urdf,
            '--output', str(rendered_folder),
            '--width', str(args.render_width),
            '--height', str(args.render_height)
        ]
        
        run_command(cmd, "Rendering hand poses")
        print(f"  → Rendered poses saved to: {rendered_folder}")
    else:
        print_header("STEP 2: Rendering Robotic Hand Poses")
        print("  ⊘ Skipped (--skip-render)")
    
    # =================================================================
    # STEP 3: Export control commands
    # =================================================================
    if not args.skip_export:
        print_header("STEP 3: Exporting Control Commands")
        
        traj_6dof_path = trajectories_folder / 'hand_trajectory_6dof.json'
        
        if args.export == 'all':
            export_formats = ['csv', 'numpy', 'text']
        else:
            export_formats = [args.export]
        
        for fmt in export_formats:
            cmd = [
                'python', 'dof6_control.py',
                '--trajectory', str(traj_6dof_path),
                '--export', fmt
            ]
            
            run_command(cmd, f"Exporting to {fmt.upper()}")
            
            # Move exported files
            if fmt == 'csv':
                src = 'control_trajectory_6dof.csv'
            elif fmt == 'numpy':
                src = 'control_trajectory_6dof.npy'
            elif fmt == 'text':
                src = 'control_trajectory_6dof.txt'
            
            if Path(src).exists():
                shutil.move(src, str(control_folder / src))
                print(f"  → Saved to: {control_folder / src}")
    else:
        print_header("STEP 3: Exporting Control Commands")
        print("  ⊘ Skipped (--skip-export)")
    
    # =================================================================
    # STEP 4: Generate motor control commands
    # =================================================================
    print_header("STEP 4: Generating Motor Control Commands")
    
    traj_6dof_path = trajectories_folder / 'hand_trajectory_6dof.json'
    motor_csv_path = control_folder / 'motor_commands.csv'
    
    if traj_6dof_path.exists():
        num_frames = generate_motor_commands(str(traj_6dof_path), str(motor_csv_path))
        print(f"✓ Generated motor commands for {num_frames} frames")
        print(f"  → Motor commands (CSV): {motor_csv_path}")
        print(f"  → Motor commands (JSON): {control_folder / 'motor_commands.json'}")
        print(f"\n  Normalization:")
        for joint, max_angle in JOINT_MAX_ANGLES.items():
            short_name = joint.replace('right_', '').replace('_joint', '')
            print(f"    {short_name}: angle / {max_angle}° → [0, 1000]")
    else:
        print(f"✗ Error: 6-DOF trajectory not found: {traj_6dof_path}")
    
    # =================================================================
    # SUMMARY
    # =================================================================
    print_header("Pipeline Complete! ✓")
    
    print("Output structure:")
    print(f"  {output_root}/")
    print(f"  ├── annotated_images/          # Original images with hand landmarks")
    print(f"  │   └── annotated_*.jpg")
    print(f"  ├── rendered_hand_poses/       # Robotic hand visualizations")
    print(f"  │   └── hand_pose_*.jpg")
    print(f"  ├── trajectories/              # Joint angle trajectories")
    print(f"  │   ├── hand_trajectory.json   (11-DOF)")
    print(f"  │   └── hand_trajectory_6dof.json  (6-DOF controllable)")
    print(f"  └── control_commands/          # Robot control files")
    
    if not args.skip_export:
        for fmt in export_formats:
            if fmt == 'csv':
                print(f"      ├── control_trajectory_6dof.csv")
            elif fmt == 'numpy':
                print(f"      ├── control_trajectory_6dof.npy")
            elif fmt == 'text':
                print(f"      ├── control_trajectory_6dof.txt")
    
    print(f"      ├── motor_commands.csv     # Motor commands [0-1000]")
    print(f"      └── motor_commands.json    # Motor commands with metadata")
    
    print(f"\n📊 Detection rate: {detected_frames}/{total_frames} frames ({100*detected_frames/total_frames:.1f}%)")
    
    # Next steps
    print(f"\n📝 Next steps:")
    print(f"  1. Review annotated images in: {annotated_folder}")
    print(f"  2. Check rendered hand poses in: {rendered_folder}")
    print(f"  3. Use 6-DOF trajectory for robot control: {trajectories_folder / 'hand_trajectory_6dof.json'}")
    print(f"  4. Send control commands to robot: {control_folder}")
    
    print(f"\n{'='*70}")
    print(f"  All done! 🎉")
    print(f"{'='*70}\n")
    
    return 0


if __name__ == '__main__':
    exit(main())
