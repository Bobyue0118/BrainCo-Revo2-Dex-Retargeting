#!/usr/bin/env python3
"""
Render robotic hand poses from trajectory
Generate images showing the retargeted hand configuration for each frame.
"""

import pybullet as p
import pybullet_data
import numpy as np
import json
from pathlib import Path
import argparse
from typing import Dict
import cv2


class HandPoseRenderer:
    """Render hand poses using PyBullet in offscreen mode."""
    
    def __init__(self, urdf_path: str, width: int = 640, height: int = 480):
        """
        Initialize renderer.
        
        Args:
            urdf_path: Path to URDF file
            width: Image width
            height: Image height
        """
        self.urdf_path = urdf_path
        self.width = width
        self.height = height
        
        # Connect to PyBullet in DIRECT mode (no GUI, faster)
        self.physics_client = p.connect(p.DIRECT)
        
        # Set up camera
        self.setup_camera()
        
        # Load URDF
        self.load_hand()

    def _client_kwargs(self) -> Dict[str, int]:
        """Return the physics client id for scoped PyBullet API calls."""
        return {"physicsClientId": self.physics_client}
        
    def setup_camera(self):
        """Setup camera parameters for rendering."""
        # Camera parameters
        self.camera_distance = 0.3
        self.camera_yaw = 270  # Correct angle for palm facing camera (from test 08)
        self.camera_pitch = -30
        self.camera_target = [0, 0, 0.1]
        
    def load_hand(self):
        """Load hand URDF."""
        p.setAdditionalSearchPath(pybullet_data.getDataPath(), **self._client_kwargs())
        
        # Load plane (for visual reference)
        p.loadURDF("plane.urdf", [0, 0, 0], **self._client_kwargs())
        
        # Load hand
        start_pos = [0, 0, 0.1]
        # Rotate hand so palm faces forward (toward camera)
        # -90° pitch + 0° yaw = palm facing camera
        start_orientation = p.getQuaternionFromEuler([-np.pi/2, 0, 0])
        
        self.hand_id = p.loadURDF(
            self.urdf_path,
            start_pos,
            start_orientation,
            useFixedBase=True,
            **self._client_kwargs(),
        )
        
        # Get joint indices
        self.joint_indices = {}
        num_joints = p.getNumJoints(self.hand_id, **self._client_kwargs())
        for i in range(num_joints):
            joint_info = p.getJointInfo(self.hand_id, i, **self._client_kwargs())
            joint_name = joint_info[1].decode('utf-8')
            joint_type = joint_info[2]
            
            if joint_type == p.JOINT_REVOLUTE:
                self.joint_indices[joint_name] = i
        
        print(f"✓ Loaded hand with {len(self.joint_indices)} controllable joints")
        
    def set_joint_angles(self, joint_angles: Dict[str, float], in_degrees: bool = True):
        """
        Set joint angles.
        
        Args:
            joint_angles: Dictionary of joint names to angles
            in_degrees: Whether input angles are in degrees
        """
        for joint_name, angle in joint_angles.items():
            if joint_name in self.joint_indices:
                joint_idx = self.joint_indices[joint_name]
                
                # Convert to radians if needed
                if in_degrees:
                    angle = np.radians(angle)
                
                p.resetJointState(
                    bodyUniqueId=self.hand_id,
                    jointIndex=joint_idx,
                    targetValue=angle,
                    **self._client_kwargs(),
                )
    
    def render(self) -> np.ndarray:
        """
        Render current hand pose to image.
        
        Returns:
            RGB image as numpy array
        """
        # Get view and projection matrices
        view_matrix = p.computeViewMatrixFromYawPitchRoll(
            cameraTargetPosition=self.camera_target,
            distance=self.camera_distance,
            yaw=self.camera_yaw,
            pitch=self.camera_pitch,
            roll=0,
            upAxisIndex=2
        )
        
        projection_matrix = p.computeProjectionMatrixFOV(
            fov=60,
            aspect=self.width / self.height,
            nearVal=0.01,
            farVal=100
        )
        
        # Render (try hardware OpenGL first, fallback to TinyRenderer)
        try:
            (_, _, px, _, _) = p.getCameraImage(
                width=self.width,
                height=self.height,
                viewMatrix=view_matrix,
                projectionMatrix=projection_matrix,
                renderer=p.ER_BULLET_HARDWARE_OPENGL,
                **self._client_kwargs(),
            )
        except:
            # Fallback to TinyRenderer if hardware OpenGL fails
            (_, _, px, _, _) = p.getCameraImage(
                width=self.width,
                height=self.height,
                viewMatrix=view_matrix,
                projectionMatrix=projection_matrix,
                renderer=p.ER_TINY_RENDERER,
                **self._client_kwargs(),
            )
        
        # Convert to RGB numpy array
        # px is returned as flat array, reshape it
        rgb_array = np.reshape(px, (self.height, self.width, 4))
        rgb_array = np.array(rgb_array, dtype=np.uint8)  # Ensure uint8 type
        rgb_array = rgb_array[:, :, :3]  # Remove alpha channel, keep RGB
        
        return rgb_array
    
    def cleanup(self):
        """Cleanup PyBullet connection."""
        p.disconnect(self.physics_client)


def render_trajectory(trajectory_path: str,
                     urdf_path: str,
                     output_folder: str,
                     width: int = 640,
                     height: int = 480):
    """
    Render all frames in trajectory.
    
    Args:
        trajectory_path: Path to trajectory JSON
        urdf_path: Path to URDF file
        output_folder: Output folder for rendered images
        width: Image width
        height: Image height
    """
    # Load trajectory
    with open(trajectory_path, 'r') as f:
        trajectory = json.load(f)
    
    frames = trajectory['frames']
    angle_unit = trajectory.get('angle_unit', 'radians')
    in_degrees = (angle_unit == 'degrees')
    
    print(f"\n{'='*60}")
    print(f"Rendering Hand Poses")
    print(f"{'='*60}")
    print(f"Trajectory: {trajectory_path}")
    print(f"URDF: {urdf_path}")
    print(f"Frames: {len(frames)}")
    print(f"Angle unit: {angle_unit}")
    print(f"Output: {output_folder}")
    print(f"{'='*60}\n")
    
    # Create output folder
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Initialize renderer
    renderer = HandPoseRenderer(urdf_path, width, height)
    
    try:
        # Render each frame
        for idx, frame_data in enumerate(frames):
            joint_angles = frame_data.get('joint_angles')
            
            if joint_angles is None:
                print(f"⚠ Frame {idx}: No hand detected, skipping")
                continue
            
            # Set joint angles
            renderer.set_joint_angles(joint_angles, in_degrees=in_degrees)
            
            # Render
            image = renderer.render()
            
            # Save image (use idx+1 to match input frame numbering)
            output_path = output_folder / f"hand_pose_{idx+1:04d}.jpg"
            cv2.imwrite(str(output_path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            
            if (idx + 1) % 10 == 0 or idx == len(frames) - 1:
                print(f"Rendered {idx + 1}/{len(frames)} frames")
        
        print(f"\n✓ Rendering complete!")
        print(f"  Output folder: {output_folder}")
        
    finally:
        renderer.cleanup()


def main():
    parser = argparse.ArgumentParser(
        description='Render robotic hand poses from trajectory',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Render trajectory to images
  python render_hand_poses.py \
      --trajectory hand_trajectory.json \
      --urdf brainco_hand/brainco_right.urdf \
      --output rendered_poses/
      
  # Custom resolution
  python render_hand_poses.py \
      --trajectory hand_trajectory.json \
      --urdf brainco_hand/brainco_right.urdf \
      --output rendered_poses/ \
      --width 1280 \
      --height 720
        """
    )
    
    parser.add_argument('--trajectory', type=str, required=True,
                       help='Path to trajectory JSON file')
    parser.add_argument('--urdf', type=str, required=True,
                       help='Path to URDF file')
    parser.add_argument('--output', type=str, required=True,
                       help='Output folder for rendered images')
    parser.add_argument('--width', type=int, default=640,
                       help='Image width (default: 640)')
    parser.add_argument('--height', type=int, default=480,
                       help='Image height (default: 480)')
    
    args = parser.parse_args()
    
    try:
        render_trajectory(
            args.trajectory,
            args.urdf,
            args.output,
            args.width,
            args.height
        )
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
