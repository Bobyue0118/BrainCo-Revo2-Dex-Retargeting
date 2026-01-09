#!/usr/bin/env python3
"""
Image-based Hand Retargeting
Process single images or image sequences to generate 6-DOF hand control trajectories.
"""

import cv2
import numpy as np
import mediapipe as mp
import json
from pathlib import Path
from typing import Dict, List, Union
import argparse
from hand_retargeting import Revo2HandRetargeting


class ImageHandRetargeting:
    """
    Retarget hand motion from images to BrainCo hand.
    Supports single image or image sequences (folders).
    """
    
    def __init__(self, urdf_path: str, hand_side: str = "right"):
        """
        Initialize image retargeting system.
        
        Args:
            urdf_path: Path to URDF file
            hand_side: "right" or "left"
        """
        self.retargeting = Revo2HandRetargeting(urdf_path, hand_side)
        self.hand_side = hand_side
        
    def process_single_image(self, image_path: str, visualize: bool = True) -> Dict:
        """
        Process a single image and return joint angles.
        
        Args:
            image_path: Path to input image
            visualize: Whether to display annotated image
            
        Returns:
            Dictionary containing joint angles and detection info
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        height, width = image.shape[:2]
        print(f"Processing image: {image_path}")
        print(f"Resolution: {width}x{height}")
        
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        with self.retargeting.mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=1,
            min_detection_confidence=0.5
        ) as hands:
            results = hands.process(image_rgb)
            
            result = {
                'image_path': image_path,
                'image_size': (width, height),
                'hand_detected': False,
                'joint_angles': None,
                'landmarks': None
            }
            
            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                result['hand_detected'] = True
                
                # Get joint angles
                joint_angles = self.retargeting.retarget_hand_pose(hand_landmarks.landmark)
                result['joint_angles'] = joint_angles
                
                # Store landmarks for visualization
                result['landmarks'] = hand_landmarks
                
                # Draw landmarks if visualize
                if visualize:
                    annotated_image = image.copy()
                    self.retargeting.mp_drawing.draw_landmarks(
                        annotated_image,
                        hand_landmarks,
                        self.retargeting.mp_hands.HAND_CONNECTIONS,
                        self.retargeting.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.retargeting.mp_drawing_styles.get_default_hand_connections_style()
                    )
                    
                    # Display joint angles in degrees
                    y_offset = 30
                    for joint_name, angle in joint_angles.items():
                        angle_deg = np.degrees(angle)
                        short_name = joint_name.replace(f'{self.hand_side}_', '')
                        text = f"{short_name}: {angle_deg:.1f}°"
                        cv2.putText(annotated_image, text, (10, y_offset),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                        y_offset += 20
                    
                    # Show image
                    cv2.imshow('Hand Detection', annotated_image)
                    print("\nPress any key to continue...")
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()
                    
                print(f"✓ Hand detected with {len(joint_angles)} joint angles")
            else:
                print("✗ No hand detected in image")
        
        return result
    
    def process_image_sequence(self, 
                              image_folder: str, 
                              output_folder: str = None,
                              save_trajectory: bool = True,
                              fps: float = 30.0,
                              image_pattern: str = "*.jpg") -> Dict:
        """
        Process a sequence of images (e.g., from a folder).
        
        Args:
            image_folder: Path to folder containing images
            output_folder: Path to save annotated images (optional)
            save_trajectory: Whether to save trajectory to JSON
            fps: Assumed frame rate for trajectory timing
            image_pattern: Glob pattern for image files (e.g., "*.jpg", "*.png")
            
        Returns:
            Trajectory dictionary
        """
        image_folder = Path(image_folder)
        if not image_folder.exists():
            raise ValueError(f"Image folder not found: {image_folder}")
        
        # Get all images matching pattern
        image_files = sorted(list(image_folder.glob(image_pattern)))
        if not image_files:
            # Try alternative patterns
            for pattern in ["*.png", "*.jpeg", "*.JPG", "*.PNG"]:
                image_files = sorted(list(image_folder.glob(pattern)))
                if image_files:
                    break
        
        if not image_files:
            raise ValueError(f"No images found in {image_folder} matching pattern {image_pattern}")
        
        print(f"\n{'='*60}")
        print(f"Processing Image Sequence")
        print(f"{'='*60}")
        print(f"Folder: {image_folder}")
        print(f"Total images: {len(image_files)}")
        print(f"Pattern: {image_pattern}")
        print(f"Assumed FPS: {fps}")
        print(f"{'='*60}\n")
        
        # Create output folder if specified
        if output_folder:
            output_folder = Path(output_folder)
            output_folder.mkdir(parents=True, exist_ok=True)
            print(f"Saving annotated images to: {output_folder}")
        
        # Initialize trajectory
        trajectory = {
            'fps': fps,
            'angle_unit': 'degrees',
            'source': 'image_sequence',
            'source_folder': str(image_folder),
            'frames': []
        }
        
        # Process each image
        with self.retargeting.mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=1,
            min_detection_confidence=0.5
        ) as hands:
            
            for idx, image_path in enumerate(image_files):
                # Read image
                image = cv2.imread(str(image_path))
                if image is None:
                    print(f"⚠ Could not read image {idx}: {image_path}")
                    continue
                
                # Convert to RGB
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # Process
                results = hands.process(image_rgb)
                
                frame_data = {
                    'frame': idx,
                    'timestamp': idx / fps,
                    'image_file': image_path.name,
                    'joint_angles': None
                }
                
                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    
                    # Get joint angles
                    joint_angles = self.retargeting.retarget_hand_pose(hand_landmarks.landmark)
                    
                    # Convert to degrees
                    joint_angles_deg = {k: np.degrees(v) for k, v in joint_angles.items()}
                    frame_data['joint_angles'] = joint_angles_deg
                    
                    # Save annotated image if output folder specified
                    if output_folder:
                        annotated_image = image.copy()
                        
                        # Draw landmarks
                        self.retargeting.mp_drawing.draw_landmarks(
                            annotated_image,
                            hand_landmarks,
                            self.retargeting.mp_hands.HAND_CONNECTIONS,
                            self.retargeting.mp_drawing_styles.get_default_hand_landmarks_style(),
                            self.retargeting.mp_drawing_styles.get_default_hand_connections_style()
                        )
                        
                        # Add frame info
                        cv2.putText(annotated_image, f"Frame: {idx}/{len(image_files)}", 
                                  (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        
                        # Save
                        output_path = output_folder / f"annotated_{image_path.name}"
                        cv2.imwrite(str(output_path), annotated_image)
                
                trajectory['frames'].append(frame_data)
                
                # Progress
                if (idx + 1) % 10 == 0 or idx == len(image_files) - 1:
                    detected = sum(1 for f in trajectory['frames'] if f['joint_angles'] is not None)
                    print(f"Processed {idx + 1}/{len(image_files)} images | "
                          f"Detected: {detected}/{idx + 1}")
        
        print(f"\n{'='*60}")
        print(f"Processing Complete!")
        print(f"{'='*60}")
        
        detected_count = sum(1 for f in trajectory['frames'] if f['joint_angles'] is not None)
        print(f"Total images: {len(image_files)}")
        print(f"Hand detected: {detected_count}/{len(image_files)} "
              f"({100*detected_count/len(image_files):.1f}%)")
        
        # Save trajectory
        if save_trajectory:
            # Save full 11 DOF trajectory
            trajectory_path = image_folder / 'hand_trajectory.json'
            with open(trajectory_path, 'w') as f:
                json.dump(trajectory, f, indent=2)
            print(f"\n✓ Trajectory saved to: {trajectory_path}")
            
            # Save 6 DOF controllable trajectory
            controllable_trajectory = self.retargeting._extract_controllable_trajectory(trajectory)
            controllable_path = image_folder / 'hand_trajectory_6dof.json'
            with open(controllable_path, 'w') as f:
                json.dump(controllable_trajectory, f, indent=2)
            print(f"✓ 6-DOF trajectory saved to: {controllable_path}")
        
        return trajectory
    
    def process_image_list(self,
                          image_paths: List[str],
                          output_path: str = None,
                          fps: float = 30.0) -> Dict:
        """
        Process a list of image paths.
        
        Args:
            image_paths: List of image file paths
            output_path: Path to save trajectory JSON (optional)
            fps: Assumed frame rate for trajectory timing
            
        Returns:
            Trajectory dictionary
        """
        print(f"\n{'='*60}")
        print(f"Processing Image List")
        print(f"{'='*60}")
        print(f"Total images: {len(image_paths)}")
        print(f"Assumed FPS: {fps}")
        print(f"{'='*60}\n")
        
        trajectory = {
            'fps': fps,
            'angle_unit': 'degrees',
            'source': 'image_list',
            'frames': []
        }
        
        with self.retargeting.mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=1,
            min_detection_confidence=0.5
        ) as hands:
            
            for idx, image_path in enumerate(image_paths):
                image = cv2.imread(image_path)
                if image is None:
                    print(f"⚠ Could not read image {idx}: {image_path}")
                    continue
                
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = hands.process(image_rgb)
                
                frame_data = {
                    'frame': idx,
                    'timestamp': idx / fps,
                    'image_file': Path(image_path).name,
                    'joint_angles': None
                }
                
                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    joint_angles = self.retargeting.retarget_hand_pose(hand_landmarks.landmark)
                    joint_angles_deg = {k: np.degrees(v) for k, v in joint_angles.items()}
                    frame_data['joint_angles'] = joint_angles_deg
                
                trajectory['frames'].append(frame_data)
                
                if (idx + 1) % 10 == 0 or idx == len(image_paths) - 1:
                    detected = sum(1 for f in trajectory['frames'] if f['joint_angles'] is not None)
                    print(f"Processed {idx + 1}/{len(image_paths)} | Detected: {detected}/{idx + 1}")
        
        detected_count = sum(1 for f in trajectory['frames'] if f['joint_angles'] is not None)
        print(f"\nTotal: {len(image_paths)} | Detected: {detected_count} "
              f"({100*detected_count/len(image_paths):.1f}%)")
        
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(trajectory, f, indent=2)
            print(f"✓ Trajectory saved to: {output_path}")
            
            # Save 6 DOF version
            controllable_trajectory = self.retargeting._extract_controllable_trajectory(trajectory)
            controllable_path = Path(output_path).parent / 'hand_trajectory_6dof.json'
            with open(controllable_path, 'w') as f:
                json.dump(controllable_trajectory, f, indent=2)
            print(f"✓ 6-DOF trajectory saved to: {controllable_path}")
        
        return trajectory


def main():
    parser = argparse.ArgumentParser(
        description='Image-based Hand Retargeting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single image
  python image_retargeting.py --image hand.jpg --urdf brainco_hand/brainco_right.urdf
  
  # Process image sequence (folder)
  python image_retargeting.py --folder images/ --urdf brainco_hand/brainco_right.urdf --output annotated/
  
  # Process with custom pattern and FPS
  python image_retargeting.py --folder frames/ --pattern "*.png" --fps 10 --urdf brainco_hand/brainco_right.urdf
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--image', type=str,
                            help='Single image file path')
    input_group.add_argument('--folder', type=str,
                            help='Folder containing image sequence')
    input_group.add_argument('--list', type=str, nargs='+',
                            help='List of image file paths')
    
    # Common options
    parser.add_argument('--urdf', type=str, required=True,
                       help='Path to URDF file')
    parser.add_argument('--hand', type=str, default='right', choices=['right', 'left'],
                       help='Hand side (right or left)')
    parser.add_argument('--output', type=str,
                       help='Output folder for annotated images (sequence mode only)')
    parser.add_argument('--fps', type=float, default=30.0,
                       help='Assumed frame rate for trajectory (default: 30.0)')
    parser.add_argument('--pattern', type=str, default='*.jpg',
                       help='Image file pattern for folder mode (default: *.jpg)')
    parser.add_argument('--no-save', action='store_true',
                       help='Do not save trajectory to JSON')
    parser.add_argument('--no-visualize', action='store_true',
                       help='Do not visualize single image result')
    
    args = parser.parse_args()
    
    # Create retargeting instance
    retargeting = ImageHandRetargeting(args.urdf, args.hand)
    
    try:
        if args.image:
            # Single image mode
            print(f"\n{'='*60}")
            print("Single Image Mode")
            print(f"{'='*60}\n")
            
            result = retargeting.process_single_image(
                args.image, 
                visualize=not args.no_visualize
            )
            
            if result['hand_detected']:
                print("\n✓ Joint Angles (degrees):")
                for joint_name, angle in result['joint_angles'].items():
                    angle_deg = np.degrees(angle)
                    print(f"  {joint_name}: {angle_deg:.2f}°")
                
                # Save to JSON if not disabled
                if not args.no_save:
                    output_json = Path(args.image).parent / 'single_image_result.json'
                    with open(output_json, 'w') as f:
                        # Convert to serializable format
                        save_data = {
                            'image_path': result['image_path'],
                            'image_size': result['image_size'],
                            'hand_detected': result['hand_detected'],
                            'joint_angles': {k: float(np.degrees(v)) 
                                           for k, v in result['joint_angles'].items()},
                            'angle_unit': 'degrees'
                        }
                        json.dump(save_data, f, indent=2)
                    print(f"\n✓ Result saved to: {output_json}")
            else:
                print("\n✗ No hand detected in image")
                return 1
                
        elif args.folder:
            # Image sequence mode
            trajectory = retargeting.process_image_sequence(
                args.folder,
                output_folder=args.output,
                save_trajectory=not args.no_save,
                fps=args.fps,
                image_pattern=args.pattern
            )
            
        elif args.list:
            # Image list mode
            output_path = None
            if not args.no_save:
                output_path = 'image_list_trajectory.json'
            
            trajectory = retargeting.process_image_list(
                args.list,
                output_path=output_path,
                fps=args.fps
            )
        
        print(f"\n{'='*60}")
        print("✓ Processing Complete!")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
