#!/usr/bin/env python3
"""
BrainCo Revo2 Hand 3D Visualizer
Visualizes the retargeted hand motion in 3D using PyBullet.
"""

import json
import time
import numpy as np
import pybullet as p
import pybullet_data
from pathlib import Path
from typing import Dict, List, Optional
import argparse


class Revo2HandVisualizer:
    """
    3D Visualizer for BrainCo Revo2 hand using PyBullet.
    """
    
    def __init__(self, urdf_path: str, use_gui: bool = True):
        """
        Initialize the visualizer.
        
        Args:
            urdf_path: Path to the URDF file
            use_gui: Whether to use GUI mode (False for headless)
        """
        self.urdf_path = urdf_path
        self.use_gui = use_gui
        
        # Initialize PyBullet
        if use_gui:
            self.physics_client = p.connect(p.GUI)
        else:
            self.physics_client = p.connect(p.DIRECT)
        
        # Set up the simulation environment
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.8)
        
        # Configure camera for better viewing angle
        # Position camera to face the palm
        p.resetDebugVisualizerCamera(
            cameraDistance=0.4,  # Slightly further back for better view
            cameraYaw=0,         # Face the palm directly
            cameraPitch=-15,     # Slight downward angle
            cameraTargetPosition=[0, 0, 0.15]  # Look at hand center
        )
        
        # Load ground plane
        self.plane_id = p.loadURDF("plane.urdf")
        
        # Load Revo2 hand
        self.hand_id = None
        self.joint_indices = {}
        self._load_hand()
        
    def _load_hand(self):
        """Load the Revo2 hand URDF."""
        # Convert URDF path to absolute path
        urdf_path = Path(self.urdf_path).resolve()
        
        # Load URDF
        start_pos = [0, 0, 0.1]
        # Rotate hand so palm faces the camera with fingertips pointing up
        # X-axis: -90° (flip upside down correction)
        # Z-axis: 90° (palm faces camera)
        start_orientation = p.getQuaternionFromEuler([-np.pi/2, 0, np.pi/2])
        
        try:
            self.hand_id = p.loadURDF(
                str(urdf_path),
                start_pos,
                start_orientation,
                useFixedBase=True
            )
            print(f"✓ Loaded Revo2 hand from: {urdf_path}")
        except Exception as e:
            print(f"✗ Error loading URDF: {e}")
            print(f"  Path: {urdf_path}")
            raise
        
        # Get joint information
        num_joints = p.getNumJoints(self.hand_id)
        print(f"Total joints in URDF: {num_joints}")
        
        # Map joint names to indices
        for i in range(num_joints):
            joint_info = p.getJointInfo(self.hand_id, i)
            joint_name = joint_info[1].decode('utf-8')
            joint_type = joint_info[2]
            
            # Only store revolute joints (type 0)
            if joint_type == p.JOINT_REVOLUTE:
                self.joint_indices[joint_name] = i
                print(f"  Joint {i}: {joint_name} (Revolute)")
        
        print(f"✓ Found {len(self.joint_indices)} controllable joints")
        
    def set_joint_angles(self, joint_angles: Dict[str, float]):
        """
        Set joint angles for the hand.
        
        Args:
            joint_angles: Dictionary of joint names to angles (in radians)
        """
        for joint_name, angle in joint_angles.items():
            if joint_name in self.joint_indices:
                joint_idx = self.joint_indices[joint_name]
                p.setJointMotorControl2(
                    bodyUniqueId=self.hand_id,
                    jointIndex=joint_idx,
                    controlMode=p.POSITION_CONTROL,
                    targetPosition=angle,
                    force=100
                )
    
    def visualize_trajectory(self, trajectory_file: str, playback_speed: float = 1.0,
                           loop: bool = False):
        """
        Visualize trajectory from JSON file.
        
        Args:
            trajectory_file: Path to trajectory JSON file
            playback_speed: Speed multiplier (1.0 = real-time)
            loop: Whether to loop the animation
        """
        # Load trajectory
        with open(trajectory_file, 'r') as f:
            trajectory = json.load(f)
        
        fps = trajectory['fps']
        frames = trajectory['frames']
        angle_unit = trajectory.get('angle_unit', 'radians')  # Default to radians for backward compatibility
        dt = 1.0 / fps / playback_speed
        
        print(f"\n{'='*60}")
        print(f"Visualizing Trajectory")
        print(f"{'='*60}")
        print(f"File: {trajectory_file}")
        print(f"Total frames: {len(frames)}")
        print(f"FPS: {fps}")
        print(f"Angle unit: {angle_unit}")
        print(f"Playback speed: {playback_speed}x")
        print(f"Loop: {loop}")
        print(f"{'='*60}\n")
        print("Controls:")
        print("  - Press 'q' to quit")
        print("  - Press SPACE to pause/resume")
        print(f"{'='*60}\n")
        
        paused = False
        frame_idx = 0
        
        try:
            while True:
                # Check for keyboard input
                keys = p.getKeyboardEvents()
                
                # Space bar to pause/resume
                if ord(' ') in keys and keys[ord(' ')] & p.KEY_WAS_TRIGGERED:
                    paused = not paused
                    print(f"{'Paused' if paused else 'Resumed'}")
                
                # 'q' to quit
                if ord('q') in keys and keys[ord('q')] & p.KEY_WAS_TRIGGERED:
                    print("Quitting...")
                    break
                
                if not paused:
                    frame_data = frames[frame_idx]
                    
                    # Only update if hand is detected
                    if frame_data['joint_angles'] is not None:
                        joint_angles = frame_data['joint_angles']
                        
                        # Convert to radians if needed (PyBullet requires radians)
                        if angle_unit == 'degrees':
                            joint_angles_rad = {k: np.radians(v) for k, v in joint_angles.items()}
                        else:
                            joint_angles_rad = joint_angles
                        
                        # Set joint angles
                        self.set_joint_angles(joint_angles_rad)
                    
                    # Display frame info
                    timestamp = frame_data['timestamp']
                    print(f"\rFrame {frame_idx + 1}/{len(frames)} | "
                          f"Time: {timestamp:.2f}s | "
                          f"Hand: {'✓' if frame_data['joint_angles'] else '✗'}",
                          end='', flush=True)
                    
                    # Move to next frame
                    frame_idx += 1
                    
                    # Loop or end
                    if frame_idx >= len(frames):
                        if loop:
                            frame_idx = 0
                            print("\n\n--- Looping ---\n")
                        else:
                            print("\n\nPlayback complete!")
                            break
                
                # Step simulation
                p.stepSimulation()
                time.sleep(dt)
                
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
    
    def visualize_pose(self, joint_angles: Dict[str, float], duration: float = 5.0):
        """
        Visualize a single pose.
        
        Args:
            joint_angles: Dictionary of joint names to angles (in degrees)
            duration: How long to display (seconds)
        """
        # Convert to radians
        joint_angles_rad = {k: np.radians(v) for k, v in joint_angles.items()}
        
        # Set pose
        self.set_joint_angles(joint_angles_rad)
        
        print(f"Displaying pose for {duration} seconds...")
        print("Press 'q' to quit early")
        
        start_time = time.time()
        while time.time() - start_time < duration:
            # Check for quit
            keys = p.getKeyboardEvents()
            if ord('q') in keys and keys[ord('q')] & p.KEY_WAS_TRIGGERED:
                break
            
            p.stepSimulation()
            time.sleep(0.01)
    
    def close(self):
        """Close the visualizer."""
        p.disconnect()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Visualize BrainCo Revo2 hand motion in 3D'
    )
    parser.add_argument('--urdf', type=str, required=True,
                       help='Path to Revo2 URDF file')
    parser.add_argument('--trajectory', type=str, default=None,
                       help='Path to trajectory JSON file')
    parser.add_argument('--speed', type=float, default=1.0,
                       help='Playback speed multiplier (default: 1.0)')
    parser.add_argument('--loop', action='store_true',
                       help='Loop the animation')
    parser.add_argument('--no-gui', action='store_true',
                       help='Run without GUI (for testing)')
    
    args = parser.parse_args()
    
    # Create visualizer
    print("\n" + "="*60)
    print("BrainCo Revo2 Hand 3D Visualizer")
    print("="*60 + "\n")
    
    visualizer = Revo2HandVisualizer(args.urdf, use_gui=not args.no_gui)
    
    try:
        if args.trajectory:
            # Visualize trajectory
            visualizer.visualize_trajectory(
                args.trajectory,
                playback_speed=args.speed,
                loop=args.loop
            )
        else:
            # Display default pose
            print("No trajectory specified. Displaying default pose.")
            print("Use --trajectory to visualize motion.")
            
            # Show a demo pose
            demo_angles = {
                'right_thumb_metacarpal_joint': 45,
                'right_thumb_proximal_joint': 20,
                'right_thumb_distal_joint': 20,
                'right_index_proximal_joint': 30,
                'right_index_distal_joint': 30,
                'right_middle_proximal_joint': 30,
                'right_middle_distal_joint': 30,
                'right_ring_proximal_joint': 30,
                'right_ring_distal_joint': 30,
                'right_pinky_proximal_joint': 30,
                'right_pinky_distal_joint': 30,
            }
            
            visualizer.visualize_pose(demo_angles, duration=10.0)
    
    finally:
        visualizer.close()
        print("\n\nVisualization ended.")


if __name__ == '__main__':
    main()
