#!/usr/bin/env python3
"""
BrainCo Hand SAPIEN Visualizer
Advanced visualization using SAPIEN simulator with realistic rendering and physics.

Note: SAPIEN may not be available on all platforms (especially macOS ARM).
      Use PyBullet (visualize_revo2_hand.py) as a fallback.
"""

import json
import time
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse
import sys

try:
    import sapien.core as sapien
    SAPIEN_AVAILABLE = True
except ImportError:
    SAPIEN_AVAILABLE = False
    sapien = None  # type: ignore


def print_sapien_installation_help():
    """Print helpful message about SAPIEN installation."""
    print("\n⚠️  SAPIEN not installed or not available on your platform.")
    print("\n" + "="*60)
    print("SAPIEN Installation Notes:")
    print("="*60)
    print("\nSAPIEN may not be available on all platforms.")
    print("\n📋 Platform Support:")
    print("  ✅ Linux (x86_64)    - pip install sapien")
    print("  ✅ Windows (x86_64)  - pip install sapien")
    print("  ⚠️  macOS (ARM M1/M2) - Not yet supported")
    print("  ⚠️  macOS (Intel)     - Limited support")
    print("\n💡 Alternative:")
    print("  Use PyBullet visualization instead:")
    print("  python visualize_revo2_hand.py --urdf <path> --trajectory <path>")
    print("\n🔗 For more info: https://sapien.ucsd.edu/")
    print("="*60 + "\n")


class SapienHandVisualizer:
    """
    Advanced 3D visualizer for BrainCo hand using SAPIEN simulator.
    Features: Realistic rendering, physics simulation, interactive camera.
    """
    
    def __init__(self, urdf_path: str, headless: bool = False):
        """
        Initialize SAPIEN visualizer.
        
        Args:
            urdf_path: Path to the URDF file
            headless: Whether to run in headless mode (no GUI)
        """
        if not SAPIEN_AVAILABLE or sapien is None:
            raise ImportError("SAPIEN is not installed or not available on this platform")
        
        self.urdf_path = Path(urdf_path).resolve()
        self.headless = headless
        
        # Initialize SAPIEN engine
        self.engine = sapien.Engine()  # type: ignore
        self.renderer = sapien.SapienRenderer()  # type: ignore
        self.engine.set_renderer(self.renderer)
        
        # Create scene
        self.scene_config = sapien.SceneConfig()  # type: ignore
        self.scene = self.engine.create_scene(self.scene_config)
        self.scene.set_timestep(1 / 240.0)  # 240Hz physics
        
        # Set up lighting
        self._setup_lighting()
        
        # Add ground
        self._add_ground()
        
        # Load hand
        self.hand: Optional[Any] = None
        self.joint_map: Dict[str, int] = {}
        self._load_hand()
        
        # Set up camera if not headless
        if not headless:
            self._setup_camera()
        
        print("✓ SAPIEN visualizer initialized")
    
    def _setup_lighting(self):
        """Set up scene lighting for realistic rendering."""
        self.scene.set_ambient_light([0.5, 0.5, 0.5])
        
        # Add directional light (sun)
        self.scene.add_directional_light(
            [0, -1, -1], 
            [0.8, 0.8, 0.8],
            shadow=True
        )
        
        # Add point lights for better illumination
        self.scene.add_point_light(
            [2, 2, 2], 
            [1, 1, 1],
            shadow=False
        )
        self.scene.add_point_light(
            [-2, 2, 2], 
            [0.8, 0.8, 0.8],
            shadow=False
        )
    
    def _add_ground(self):
        """Add ground plane to the scene."""
        ground_material = self.renderer.create_material()
        ground_material.base_color = [0.2, 0.2, 0.2, 1.0]
        ground_material.metallic = 0.0
        ground_material.roughness = 0.7
        
        self.scene.add_ground(
            altitude=0,
            render_material=ground_material
        )
    
    def _load_hand(self):
        """Load the hand URDF into SAPIEN."""
        loader = self.scene.create_urdf_loader()
        loader.fix_root_link = True
        
        try:
            self.hand = loader.load(str(self.urdf_path))
            self.hand.set_root_pose(sapien.Pose([0, 0, 0.1], [1, 0, 0, 0]))
            
            print(f"✓ Loaded hand from: {self.urdf_path}")
            
            # Create joint mapping
            self._create_joint_map()
            
        except Exception as e:
            print(f"✗ Error loading URDF: {e}")
            raise
    
    def _create_joint_map(self):
        """Create mapping from joint names to joint indices."""
        joints = self.hand.get_active_joints()
        
        print(f"Found {len(joints)} active joints:")
        for i, joint in enumerate(joints):
            joint_name = joint.get_name()
            self.joint_map[joint_name] = i
            
            # Get joint limits
            limits = joint.get_limits()
            print(f"  {i}: {joint_name} - Limits: [{limits[0][0]:.3f}, {limits[1][0]:.3f}]")
        
        print(f"✓ Created joint map with {len(self.joint_map)} joints")
    
    def _setup_camera(self):
        """Set up the camera for visualization."""
        self.camera_mount_actor = self.scene.create_actor_builder().build_kinematic()
        self.camera = self.scene.add_mounted_camera(
            name="main_camera",
            actor=self.camera_mount_actor,
            pose=sapien.Pose([0.3, 0.3, 0.2], [0.924, 0, 0.383, 0]),
            width=1280,
            height=720,
            fovy=np.deg2rad(45),
            near=0.01,
            far=10
        )
        
        print("✓ Camera configured")
    
    def set_joint_angles(self, joint_angles: Dict[str, float]):
        """
        Set joint angles for the hand.
        
        Args:
            joint_angles: Dictionary mapping joint names to angles (radians)
        """
        if not self.hand:
            return
        
        joints = self.hand.get_active_joints()
        qpos = np.zeros(len(joints))
        
        for joint_name, angle in joint_angles.items():
            if joint_name in self.joint_map:
                idx = self.joint_map[joint_name]
                qpos[idx] = angle
        
        self.hand.set_qpos(qpos)
    
    def step(self):
        """Step the simulation forward."""
        self.scene.step()
        if not self.headless:
            self.scene.update_render()
    
    def render(self) -> Optional[np.ndarray]:
        """
        Render the current scene.
        
        Returns:
            RGB image if not headless, None otherwise
        """
        if self.headless:
            return None
        
        self.camera.take_picture()
        rgba = self.camera.get_float_texture('Color')
        rgb = (rgba[..., :3] * 255).astype(np.uint8)
        return rgb
    
    def load_trajectory(self, trajectory_path: str) -> List[Dict[str, float]]:
        """
        Load trajectory from JSON file.
        
        Args:
            trajectory_path: Path to trajectory JSON file
            
        Returns:
            List of joint angle dictionaries
        """
        with open(trajectory_path, 'r') as f:
            data = json.load(f)
        
        frames = data.get('frames', [])
        print(f"✓ Loaded trajectory with {len(frames)} frames")
        
        return frames
    
    def replay_trajectory(self, trajectory: List[Dict[str, float]], 
                         speed: float = 1.0, loop: bool = False):
        """
        Replay a trajectory in the visualizer.
        
        Args:
            trajectory: List of joint angle dictionaries
            speed: Playback speed multiplier
            loop: Whether to loop the trajectory
        """
        if not trajectory:
            print("✗ Empty trajectory")
            return
        
        frame_time = 1.0 / 30.0 / speed  # Assuming 30 FPS
        frame_idx = 0
        
        print(f"\n▶ Playing trajectory ({len(trajectory)} frames)")
        print(f"  Speed: {speed}x, Loop: {loop}")
        print("\nControls:")
        print("  Q: Quit")
        print("  SPACE: Pause/Resume")
        print("  ←/→: Skip frames")
        print("\n" + "="*50)
        
        paused = False
        
        try:
            while True:
                if not paused:
                    # Get current frame
                    frame = trajectory[frame_idx]
                    
                    # Set joint angles
                    self.set_joint_angles(frame)
                    
                    # Update simulation
                    self.step()
                    
                    # Render
                    if not self.headless:
                        img = self.render()
                        # TODO: Display image using cv2 or other method
                    
                    # Progress indicator
                    if frame_idx % 30 == 0:
                        progress = (frame_idx + 1) / len(trajectory) * 100
                        print(f"\rFrame {frame_idx + 1}/{len(trajectory)} ({progress:.1f}%)", 
                              end='', flush=True)
                    
                    # Move to next frame
                    frame_idx += 1
                    
                    # Check loop
                    if frame_idx >= len(trajectory):
                        if loop:
                            frame_idx = 0
                            print("\n\n↺ Looping trajectory...")
                        else:
                            print("\n\n✓ Trajectory playback complete!")
                            break
                    
                    # Wait for frame time
                    time.sleep(frame_time)
                else:
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            print("\n\n⏹ Playback stopped by user")
    
    def cleanup(self):
        """Clean up resources."""
        print("\n🧹 Cleaning up SAPIEN resources...")
        # SAPIEN cleanup is handled automatically


def main():
    parser = argparse.ArgumentParser(
        description="Visualize BrainCo hand trajectory using SAPIEN simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python visualize_sapien.py --urdf brainco_hand/brainco_right.urdf --trajectory hand_trajectory.json
  
  # With custom speed and looping
  python visualize_sapien.py --urdf brainco_hand/brainco_right.urdf --trajectory hand_trajectory.json --speed 0.5 --loop
  
  # Headless mode (no visualization)
  python visualize_sapien.py --urdf brainco_hand/brainco_right.urdf --trajectory hand_trajectory.json --headless
        """
    )
    
    parser.add_argument('--urdf', type=str, required=True,
                       help='Path to URDF file')
    parser.add_argument('--trajectory', type=str, required=True,
                       help='Path to trajectory JSON file')
    parser.add_argument('--speed', type=float, default=1.0,
                       help='Playback speed multiplier (default: 1.0)')
    parser.add_argument('--loop', action='store_true',
                       help='Loop trajectory playback')
    parser.add_argument('--headless', action='store_true',
                       help='Run without GUI (headless mode)')
    
    args = parser.parse_args()
    
    # Check if SAPIEN is available
    if not SAPIEN_AVAILABLE:
        print_sapien_installation_help()
        print("\n💡 TIP: Use PyBullet instead:")
        print("  python visualize_revo2_hand.py \\")
        print(f"      --urdf \"{args.urdf}\" \\")
        print(f"      --trajectory \"{args.trajectory}\"")
        if args.loop:
            print("      --loop")
        print()
        return 1
    
    # Check files exist
    if not Path(args.urdf).exists():
        print(f"✗ Error: URDF file not found: {args.urdf}")
        return 1
    
    if not Path(args.trajectory).exists():
        print(f"✗ Error: Trajectory file not found: {args.trajectory}")
        return 1
    
    print("\n" + "="*60)
    print("BrainCo Hand SAPIEN Visualizer")
    print("="*60)
    
    try:
        # Initialize visualizer
        visualizer = SapienHandVisualizer(args.urdf, headless=args.headless)
        
        # Load trajectory
        trajectory = visualizer.load_trajectory(args.trajectory)
        
        # Replay trajectory
        visualizer.replay_trajectory(
            trajectory,
            speed=args.speed,
            loop=args.loop
        )
        
        # Cleanup
        visualizer.cleanup()
        
        print("\n✓ Visualization complete!")
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⏹ Interrupted by user")
        return 130
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
