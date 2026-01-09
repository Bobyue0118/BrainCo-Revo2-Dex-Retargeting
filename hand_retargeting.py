#!/usr/bin/env python3
"""
Human Hand to BrainCo Revo2 Hand Retargeting Script
This script uses MediaPipe for hand tracking from video and retargets the motion to Revo2 robotic hand.
"""

import cv2
import numpy as np
import mediapipe as mp
import json
from pathlib import Path
from typing import Dict, List, Tuple
import xml.etree.ElementTree as ET


class Revo2HandRetargeting:
    """
    Retargets human hand motion from video to BrainCo Revo2 robotic hand.
    """
    
    def __init__(self, urdf_path: str, hand_side: str = "right"):
        """
        Initialize the retargeting system.
        
        Args:
            urdf_path: Path to the URDF file
            hand_side: "right" or "left"
        """
        self.hand_side = hand_side
        self.urdf_path = urdf_path
        
        # Initialize MediaPipe Hand detector
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # MediaPipe hand landmarks indices
        self.WRIST = 0
        self.THUMB_CMC = 1
        self.THUMB_MCP = 2
        self.THUMB_IP = 3
        self.THUMB_TIP = 4
        self.INDEX_MCP = 5
        self.INDEX_PIP = 6
        self.INDEX_DIP = 7
        self.INDEX_TIP = 8
        self.MIDDLE_MCP = 9
        self.MIDDLE_PIP = 10
        self.MIDDLE_DIP = 11
        self.MIDDLE_TIP = 12
        self.RING_MCP = 13
        self.RING_PIP = 14
        self.RING_DIP = 15
        self.RING_TIP = 16
        self.PINKY_MCP = 17
        self.PINKY_PIP = 18
        self.PINKY_DIP = 19
        self.PINKY_TIP = 20
        
        # Parse URDF to get joint limits
        self.joint_limits = self._parse_urdf_joint_limits()
        
        # Parse mimic joints to identify controllable DOFs
        self.mimic_joints = self._parse_mimic_joints()
        
        # Revo2 joint names (for right hand) - 11 DOF total
        self.revo2_joints = {
            'thumb_metacarpal': f'{hand_side}_thumb_metacarpal_joint',
            'thumb_proximal': f'{hand_side}_thumb_proximal_joint',
            'thumb_distal': f'{hand_side}_thumb_distal_joint',
            'index_proximal': f'{hand_side}_index_proximal_joint',
            'index_distal': f'{hand_side}_index_distal_joint',
            'middle_proximal': f'{hand_side}_middle_proximal_joint',
            'middle_distal': f'{hand_side}_middle_distal_joint',
            'ring_proximal': f'{hand_side}_ring_proximal_joint',
            'ring_distal': f'{hand_side}_ring_distal_joint',
            'pinky_proximal': f'{hand_side}_pinky_proximal_joint',
            'pinky_distal': f'{hand_side}_pinky_distal_joint',
        }
        
        # Controllable joints only (6 DOF for BrainCo with mimic)
        # Thumb: 2 DOF (metacarpal + proximal, distal mimics proximal)
        # Other fingers: 1 DOF each (proximal, distal mimics proximal)
        self.controllable_joints = {
            'thumb_metacarpal': f'{hand_side}_thumb_metacarpal_joint',
            'thumb_proximal': f'{hand_side}_thumb_proximal_joint',
            'index_proximal': f'{hand_side}_index_proximal_joint',
            'middle_proximal': f'{hand_side}_middle_proximal_joint',
            'ring_proximal': f'{hand_side}_ring_proximal_joint',
            'pinky_proximal': f'{hand_side}_pinky_proximal_joint',
        }
        
    def _parse_urdf_joint_limits(self) -> Dict[str, Tuple[float, float]]:
        """Parse URDF file to extract joint limits."""
        tree = ET.parse(self.urdf_path)
        root = tree.getroot()
        
        joint_limits = {}
        for joint in root.findall('.//joint[@type="revolute"]'):
            joint_name = joint.get('name')
            limit = joint.find('limit')
            if limit is not None:
                lower = float(limit.get('lower', 0))
                upper = float(limit.get('upper', 0))
                joint_limits[joint_name] = (lower, upper)
        
        return joint_limits
    
    def _parse_mimic_joints(self) -> Dict[str, Dict[str, any]]:
        """
        Parse URDF file to extract mimic joint relationships.
        
        Returns:
            Dictionary mapping joint names to mimic info:
            {joint_name: {'parent': parent_joint, 'multiplier': mul, 'offset': off}}
        """
        tree = ET.parse(self.urdf_path)
        root = tree.getroot()
        
        mimic_joints = {}
        for joint in root.findall('.//joint[@type="revolute"]'):
            joint_name = joint.get('name')
            mimic = joint.find('mimic')
            if mimic is not None:
                parent_joint = mimic.get('joint')
                multiplier = float(mimic.get('multiplier', 1.0))
                offset = float(mimic.get('offset', 0.0))
                mimic_joints[joint_name] = {
                    'parent': parent_joint,
                    'multiplier': multiplier,
                    'offset': offset
                }
        
        return mimic_joints
    
    def _calculate_angle(self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
        """
        Calculate angle between three points (p1-p2-p3).
        
        Args:
            p1, p2, p3: 3D points as numpy arrays
            
        Returns:
            Angle in radians
        """
        v1 = p1 - p2
        v2 = p3 - p2
        
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        angle = np.arccos(cos_angle)
        
        return angle
    
    def _calculate_finger_curl(self, landmarks, mcp_idx: int, pip_idx: int, 
                               dip_idx: int, tip_idx: int) -> Tuple[float, float]:
        """
        Calculate proximal and distal joint angles for a finger.
        
        Returns:
            (proximal_angle, distal_angle) in radians
        """
        # Convert landmarks to numpy arrays
        mcp = np.array([landmarks[mcp_idx].x, landmarks[mcp_idx].y, landmarks[mcp_idx].z])
        pip = np.array([landmarks[pip_idx].x, landmarks[pip_idx].y, landmarks[pip_idx].z])
        dip = np.array([landmarks[dip_idx].x, landmarks[dip_idx].y, landmarks[dip_idx].z])
        tip = np.array([landmarks[tip_idx].x, landmarks[tip_idx].y, landmarks[tip_idx].z])
        
        # Calculate joint angles (bend angles)
        proximal_angle = np.pi - self._calculate_angle(mcp, pip, dip)
        distal_angle = np.pi - self._calculate_angle(pip, dip, tip)
        
        return proximal_angle, distal_angle
    
    def _calculate_thumb_angles(self, landmarks) -> Tuple[float, float, float]:
        """
        Calculate thumb joint angles.
        
        Returns:
            (metacarpal_angle, proximal_angle, distal_angle) in radians
        """
        wrist = np.array([landmarks[self.WRIST].x, landmarks[self.WRIST].y, landmarks[self.WRIST].z])
        cmc = np.array([landmarks[self.THUMB_CMC].x, landmarks[self.THUMB_CMC].y, landmarks[self.THUMB_CMC].z])
        mcp = np.array([landmarks[self.THUMB_MCP].x, landmarks[self.THUMB_MCP].y, landmarks[self.THUMB_MCP].z])
        ip = np.array([landmarks[self.THUMB_IP].x, landmarks[self.THUMB_IP].y, landmarks[self.THUMB_IP].z])
        tip = np.array([landmarks[self.THUMB_TIP].x, landmarks[self.THUMB_TIP].y, landmarks[self.THUMB_TIP].z])
        
        # Calculate thumb abduction/adduction (metacarpal joint)
        index_mcp = np.array([landmarks[self.INDEX_MCP].x, landmarks[self.INDEX_MCP].y, landmarks[self.INDEX_MCP].z])
        
        # Thumb metacarpal angle (CMC joint)
        metacarpal_angle = self._calculate_angle(wrist, cmc, mcp) - np.pi/2
        metacarpal_angle = np.clip(metacarpal_angle, 0, np.pi/2)
        
        # Thumb flexion angles
        proximal_angle = np.pi - self._calculate_angle(cmc, mcp, ip)
        distal_angle = np.pi - self._calculate_angle(mcp, ip, tip)
        
        return metacarpal_angle, proximal_angle, distal_angle
    
    def _apply_joint_limits(self, joint_name: str, angle: float) -> float:
        """Apply joint limits from URDF."""
        if joint_name in self.joint_limits:
            lower, upper = self.joint_limits[joint_name]
            return np.clip(angle, lower, upper)
        return angle
    
    def retarget_hand_pose(self, landmarks) -> Dict[str, float]:
        """
        Convert MediaPipe hand landmarks to Revo2 joint angles.
        
        Args:
            landmarks: MediaPipe hand landmarks
            
        Returns:
            Dictionary of joint names to angles (in radians)
        """
        joint_angles = {}
        
        # Thumb
        thumb_meta, thumb_prox, thumb_dist = self._calculate_thumb_angles(landmarks)
        joint_angles[self.revo2_joints['thumb_metacarpal']] = self._apply_joint_limits(
            self.revo2_joints['thumb_metacarpal'], thumb_meta
        )
        joint_angles[self.revo2_joints['thumb_proximal']] = self._apply_joint_limits(
            self.revo2_joints['thumb_proximal'], thumb_prox
        )
        joint_angles[self.revo2_joints['thumb_distal']] = self._apply_joint_limits(
            self.revo2_joints['thumb_distal'], thumb_dist
        )
        
        # Index finger
        index_prox, index_dist = self._calculate_finger_curl(
            landmarks, self.INDEX_MCP, self.INDEX_PIP, self.INDEX_DIP, self.INDEX_TIP
        )
        joint_angles[self.revo2_joints['index_proximal']] = self._apply_joint_limits(
            self.revo2_joints['index_proximal'], index_prox
        )
        joint_angles[self.revo2_joints['index_distal']] = self._apply_joint_limits(
            self.revo2_joints['index_distal'], index_dist
        )
        
        # Middle finger
        middle_prox, middle_dist = self._calculate_finger_curl(
            landmarks, self.MIDDLE_MCP, self.MIDDLE_PIP, self.MIDDLE_DIP, self.MIDDLE_TIP
        )
        joint_angles[self.revo2_joints['middle_proximal']] = self._apply_joint_limits(
            self.revo2_joints['middle_proximal'], middle_prox
        )
        joint_angles[self.revo2_joints['middle_distal']] = self._apply_joint_limits(
            self.revo2_joints['middle_distal'], middle_dist
        )
        
        # Ring finger
        ring_prox, ring_dist = self._calculate_finger_curl(
            landmarks, self.RING_MCP, self.RING_PIP, self.RING_DIP, self.RING_TIP
        )
        joint_angles[self.revo2_joints['ring_proximal']] = self._apply_joint_limits(
            self.revo2_joints['ring_proximal'], ring_prox
        )
        joint_angles[self.revo2_joints['ring_distal']] = self._apply_joint_limits(
            self.revo2_joints['ring_distal'], ring_dist
        )
        
        # Pinky finger
        pinky_prox, pinky_dist = self._calculate_finger_curl(
            landmarks, self.PINKY_MCP, self.PINKY_PIP, self.PINKY_DIP, self.PINKY_TIP
        )
        joint_angles[self.revo2_joints['pinky_proximal']] = self._apply_joint_limits(
            self.revo2_joints['pinky_proximal'], pinky_prox
        )
        joint_angles[self.revo2_joints['pinky_distal']] = self._apply_joint_limits(
            self.revo2_joints['pinky_distal'], pinky_dist
        )
        
        return joint_angles
    
    def process_video(self, video_path: str, output_path: str = None, 
                     save_trajectory: bool = True):
        """
        Process video file and extract hand joint trajectories.
        
        Args:
            video_path: Path to input video
            output_path: Path to save annotated video (optional)
            save_trajectory: Whether to save joint angle trajectory to JSON
        """
        cap = cv2.VideoCapture(video_path)
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"Processing video: {video_path}")
        print(f"Resolution: {width}x{height}, FPS: {fps}, Total frames: {total_frames}")
        
        # Initialize video writer if output path is specified
        out = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Storage for trajectory
        trajectory = {
            'fps': fps,
            'angle_unit': 'degrees',  # Angles stored in degrees for readability
            'frames': []
        }
        
        # Initialize MediaPipe Hands
        with self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as hands:
            
            frame_idx = 0
            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    break
                
                # Convert BGR to RGB
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                
                # Process the image
                results = hands.process(image)
                
                # Convert back to BGR for display
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                
                frame_data = {
                    'frame': frame_idx,
                    'timestamp': frame_idx / fps,
                    'joint_angles': None
                }
                
                # Process hand landmarks
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Draw hand landmarks on the image
                        self.mp_drawing.draw_landmarks(
                            image,
                            hand_landmarks,
                            self.mp_hands.HAND_CONNECTIONS,
                            self.mp_drawing_styles.get_default_hand_landmarks_style(),
                            self.mp_drawing_styles.get_default_hand_connections_style()
                        )
                        
                        # Retarget to Revo2 joint angles
                        joint_angles = self.retarget_hand_pose(hand_landmarks.landmark)
                        
                        # Convert to degrees for storage (more human-readable)
                        joint_angles_deg = {k: np.degrees(v) for k, v in joint_angles.items()}
                        
                        # Save joint angles in DEGREES (human-readable format)
                        frame_data['joint_angles'] = joint_angles_deg
                        
                        # Display joint angles on frame
                        y_offset = 30
                        for joint_name, angle in joint_angles_deg.items():
                            # Shorten joint name for display
                            short_name = joint_name.replace(f'{self.hand_side}_', '')
                            text = f"{short_name}: {angle:.1f}°"
                            cv2.putText(image, text, (10, y_offset), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                            y_offset += 20
                
                # Add frame number
                cv2.putText(image, f"Frame: {frame_idx}/{total_frames}", 
                          (width - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                          0.6, (255, 255, 255), 2)
                
                # Save frame
                if out:
                    out.write(image)
                
                # Save frame data
                trajectory['frames'].append(frame_data)
                
                # Display
                cv2.imshow('Hand Retargeting', image)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                frame_idx += 1
                
                # Progress indicator
                if frame_idx % 30 == 0:
                    print(f"Processed {frame_idx}/{total_frames} frames...")
        
        # Cleanup
        cap.release()
        if out:
            out.release()
        cv2.destroyAllWindows()
        
        print(f"\nProcessing complete! Processed {frame_idx} frames.")
        
        # Save trajectory to JSON
        if save_trajectory:
            # Save full 11 DOF trajectory
            trajectory_path = Path(video_path).parent / 'hand_trajectory.json'
            with open(trajectory_path, 'w') as f:
                json.dump(trajectory, f, indent=2)
            print(f"Trajectory saved to: {trajectory_path}")
            
            # Save controllable 6 DOF trajectory (for actual robot control)
            controllable_trajectory = self._extract_controllable_trajectory(trajectory)
            controllable_path = Path(video_path).parent / 'hand_trajectory_6dof.json'
            with open(controllable_path, 'w') as f:
                json.dump(controllable_trajectory, f, indent=2)
            print(f"6-DOF controllable trajectory saved to: {controllable_path}")
        
        return trajectory
    
    def _extract_controllable_trajectory(self, full_trajectory: Dict) -> Dict:
        """
        Extract only the controllable joints (6 DOF) from full 11 DOF trajectory.
        
        Args:
            full_trajectory: Full 11 DOF trajectory data
            
        Returns:
            6 DOF controllable trajectory
        """
        controllable_traj = {
            'fps': full_trajectory['fps'],
            'dof': 6,
            'angle_unit': 'degrees',  # Angles in degrees for readability
            'joints': list(self.controllable_joints.keys()),
            'joint_names': list(self.controllable_joints.values()),
            'mimic_info': {},
            'frames': []
        }
        
        # Add mimic information
        for joint_name, mimic_info in self.mimic_joints.items():
            controllable_traj['mimic_info'][joint_name] = mimic_info
        
        # Extract controllable joint angles from each frame
        for frame in full_trajectory['frames']:
            controllable_frame = {}
            # Access joint_angles from frame data
            if 'joint_angles' in frame and frame['joint_angles']:
                for key, joint_name in self.controllable_joints.items():
                    if joint_name in frame['joint_angles']:
                        controllable_frame[joint_name] = frame['joint_angles'][joint_name]
            controllable_traj['frames'].append(controllable_frame)
        
        return controllable_traj


def main():
    """Main function to run the retargeting."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Human Hand to Revo2 Hand Retargeting')
    parser.add_argument('--video', type=str, required=True,
                       help='Path to input video file')
    parser.add_argument('--urdf', type=str, required=True,
                       help='Path to Revo2 URDF file')
    parser.add_argument('--hand', type=str, default='right', choices=['right', 'left'],
                       help='Hand side (right or left)')
    parser.add_argument('--output', type=str, default=None,
                       help='Path to save annotated output video')
    parser.add_argument('--no-save-trajectory', action='store_true',
                       help='Do not save joint angle trajectory')
    
    args = parser.parse_args()
    
    # Create retargeting instance
    retargeting = Revo2HandRetargeting(args.urdf, args.hand)
    
    # Process video
    retargeting.process_video(
        args.video, 
        args.output,
        save_trajectory=not args.no_save_trajectory
    )


if __name__ == '__main__':
    main()
