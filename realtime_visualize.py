#!/usr/bin/env python3
"""
Real-time Hand Retargeting with 3D Visualization
Processes video and shows both the original video and the retargeted Revo2 hand in 3D.
"""

import cv2
import numpy as np
import mediapipe as mp
import pybullet as p
import pybullet_data
import json
import time
from pathlib import Path
from typing import Dict
import xml.etree.ElementTree as ET
import argparse


class RealtimeRetargetingVisualizer:
    """
    Real-time hand retargeting with side-by-side video and 3D visualization.
    """
    
    def __init__(self, urdf_path: str, hand_side: str = "right"):
        """
        Initialize the system.
        
        Args:
            urdf_path: Path to the URDF file
            hand_side: "right" or "left"
        """
        self.hand_side = hand_side
        self.urdf_path = urdf_path
        
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # MediaPipe landmarks
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
        
        # Revo2 joint names
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
        
        # Parse URDF for joint limits
        self.joint_limits = self._parse_urdf_joint_limits()
        
        # Initialize PyBullet
        self._init_pybullet()
        
    def _parse_urdf_joint_limits(self):
        """Parse URDF to get joint limits."""
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
    
    def _init_pybullet(self):
        """Initialize PyBullet simulation."""
        self.physics_client = p.connect(p.GUI)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.8)
        
        # Configure camera for better view
        p.resetDebugVisualizerCamera(
            cameraDistance=0.3,
            cameraYaw=45,
            cameraPitch=-30,
            cameraTargetPosition=[0, 0, 0.1]
        )
        
        # Load ground plane
        self.plane_id = p.loadURDF("plane.urdf")
        
        # Load hand
        urdf_path = Path(self.urdf_path).resolve()
        start_pos = [0, 0, 0.1]
        # Rotate hand so palm faces the camera with fingertips pointing up
        # X-axis: -90° (flip upside down correction)
        # Z-axis: 90° (palm faces camera)
        start_orientation = p.getQuaternionFromEuler([-np.pi/2, 0, np.pi/2])
        
        self.hand_id = p.loadURDF(
            str(urdf_path),
            start_pos,
            start_orientation,
            useFixedBase=True
        )
        
        # Map joint names to indices
        self.joint_indices = {}
        num_joints = p.getNumJoints(self.hand_id)
        
        for i in range(num_joints):
            joint_info = p.getJointInfo(self.hand_id, i)
            joint_name = joint_info[1].decode('utf-8')
            joint_type = joint_info[2]
            
            if joint_type == p.JOINT_REVOLUTE:
                self.joint_indices[joint_name] = i
        
        print(f"✓ PyBullet initialized with {len(self.joint_indices)} joints")
    
    def _calculate_angle(self, p1, p2, p3):
        """Calculate angle between three points."""
        v1 = p1 - p2
        v2 = p3 - p2
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        return np.arccos(cos_angle)
    
    def _calculate_finger_curl(self, landmarks, mcp_idx, pip_idx, dip_idx, tip_idx):
        """Calculate finger joint angles."""
        mcp = np.array([landmarks[mcp_idx].x, landmarks[mcp_idx].y, landmarks[mcp_idx].z])
        pip = np.array([landmarks[pip_idx].x, landmarks[pip_idx].y, landmarks[pip_idx].z])
        dip = np.array([landmarks[dip_idx].x, landmarks[dip_idx].y, landmarks[dip_idx].z])
        tip = np.array([landmarks[tip_idx].x, landmarks[tip_idx].y, landmarks[tip_idx].z])
        
        proximal_angle = np.pi - self._calculate_angle(mcp, pip, dip)
        distal_angle = np.pi - self._calculate_angle(pip, dip, tip)
        
        return proximal_angle, distal_angle
    
    def _calculate_thumb_angles(self, landmarks):
        """Calculate thumb joint angles."""
        wrist = np.array([landmarks[self.WRIST].x, landmarks[self.WRIST].y, landmarks[self.WRIST].z])
        cmc = np.array([landmarks[self.THUMB_CMC].x, landmarks[self.THUMB_CMC].y, landmarks[self.THUMB_CMC].z])
        mcp = np.array([landmarks[self.THUMB_MCP].x, landmarks[self.THUMB_MCP].y, landmarks[self.THUMB_MCP].z])
        ip = np.array([landmarks[self.THUMB_IP].x, landmarks[self.THUMB_IP].y, landmarks[self.THUMB_IP].z])
        tip = np.array([landmarks[self.THUMB_TIP].x, landmarks[self.THUMB_TIP].y, landmarks[self.THUMB_TIP].z])
        
        metacarpal_angle = self._calculate_angle(wrist, cmc, mcp) - np.pi/2
        metacarpal_angle = np.clip(metacarpal_angle, 0, np.pi/2)
        
        proximal_angle = np.pi - self._calculate_angle(cmc, mcp, ip)
        distal_angle = np.pi - self._calculate_angle(mcp, ip, tip)
        
        return metacarpal_angle, proximal_angle, distal_angle
    
    def _apply_joint_limits(self, joint_name, angle):
        """Apply joint limits."""
        if joint_name in self.joint_limits:
            lower, upper = self.joint_limits[joint_name]
            return np.clip(angle, lower, upper)
        return angle
    
    def retarget_hand_pose(self, landmarks):
        """Convert MediaPipe landmarks to Revo2 joint angles."""
        joint_angles = {}
        
        # Thumb
        thumb_meta, thumb_prox, thumb_dist = self._calculate_thumb_angles(landmarks)
        joint_angles[self.revo2_joints['thumb_metacarpal']] = self._apply_joint_limits(
            self.revo2_joints['thumb_metacarpal'], thumb_meta)
        joint_angles[self.revo2_joints['thumb_proximal']] = self._apply_joint_limits(
            self.revo2_joints['thumb_proximal'], thumb_prox)
        joint_angles[self.revo2_joints['thumb_distal']] = self._apply_joint_limits(
            self.revo2_joints['thumb_distal'], thumb_dist)
        
        # Index
        index_prox, index_dist = self._calculate_finger_curl(
            landmarks, self.INDEX_MCP, self.INDEX_PIP, self.INDEX_DIP, self.INDEX_TIP)
        joint_angles[self.revo2_joints['index_proximal']] = self._apply_joint_limits(
            self.revo2_joints['index_proximal'], index_prox)
        joint_angles[self.revo2_joints['index_distal']] = self._apply_joint_limits(
            self.revo2_joints['index_distal'], index_dist)
        
        # Middle
        middle_prox, middle_dist = self._calculate_finger_curl(
            landmarks, self.MIDDLE_MCP, self.MIDDLE_PIP, self.MIDDLE_DIP, self.MIDDLE_TIP)
        joint_angles[self.revo2_joints['middle_proximal']] = self._apply_joint_limits(
            self.revo2_joints['middle_proximal'], middle_prox)
        joint_angles[self.revo2_joints['middle_distal']] = self._apply_joint_limits(
            self.revo2_joints['middle_distal'], middle_dist)
        
        # Ring
        ring_prox, ring_dist = self._calculate_finger_curl(
            landmarks, self.RING_MCP, self.RING_PIP, self.RING_DIP, self.RING_TIP)
        joint_angles[self.revo2_joints['ring_proximal']] = self._apply_joint_limits(
            self.revo2_joints['ring_proximal'], ring_prox)
        joint_angles[self.revo2_joints['ring_distal']] = self._apply_joint_limits(
            self.revo2_joints['ring_distal'], ring_dist)
        
        # Pinky
        pinky_prox, pinky_dist = self._calculate_finger_curl(
            landmarks, self.PINKY_MCP, self.PINKY_PIP, self.PINKY_DIP, self.PINKY_TIP)
        joint_angles[self.revo2_joints['pinky_proximal']] = self._apply_joint_limits(
            self.revo2_joints['pinky_proximal'], pinky_prox)
        joint_angles[self.revo2_joints['pinky_distal']] = self._apply_joint_limits(
            self.revo2_joints['pinky_distal'], pinky_dist)
        
        return joint_angles
    
    def set_joint_angles(self, joint_angles):
        """Set joint angles in PyBullet."""
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
    
    def process_video(self, video_path: str):
        """
        Process video with real-time 3D visualization.
        
        Args:
            video_path: Path to input video
        """
        cap = cv2.VideoCapture(video_path)
        
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"\n{'='*60}")
        print(f"Real-time Hand Retargeting with 3D Visualization")
        print(f"{'='*60}")
        print(f"Video: {video_path}")
        print(f"FPS: {fps}, Total frames: {total_frames}")
        print(f"\nControls:")
        print(f"  - Press 'q' to quit")
        print(f"  - Press SPACE to pause/resume")
        print(f"{'='*60}\n")
        
        with self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as hands:
            
            frame_idx = 0
            paused = False
            
            while cap.isOpened():
                if not paused:
                    success, frame = cap.read()
                    if not success:
                        break
                    
                    # Process frame
                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image.flags.writeable = False
                    results = hands.process(image)
                    image.flags.writeable = True
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    
                    # Draw landmarks
                    if results.multi_hand_landmarks:
                        for hand_landmarks in results.multi_hand_landmarks:
                            self.mp_drawing.draw_landmarks(
                                image,
                                hand_landmarks,
                                self.mp_hands.HAND_CONNECTIONS,
                                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                                self.mp_drawing_styles.get_default_hand_connections_style()
                            )
                            
                            # Retarget and update 3D hand
                            joint_angles = self.retarget_hand_pose(hand_landmarks.landmark)
                            self.set_joint_angles(joint_angles)
                    
                    # Add info text
                    cv2.putText(image, f"Frame: {frame_idx}/{total_frames}", 
                              (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(image, "Press SPACE to pause, 'q' to quit", 
                              (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                    
                    # Display video
                    cv2.imshow('Hand Tracking', image)
                    frame_idx += 1
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord(' '):
                    paused = not paused
                    print(f"{'Paused' if paused else 'Resumed'}")
                
                # Step simulation
                p.stepSimulation()
                time.sleep(1.0 / fps)
        
        cap.release()
        cv2.destroyAllWindows()
        print(f"\n✓ Processing complete! Processed {frame_idx} frames.")
    
    def close(self):
        """Close the visualizer."""
        p.disconnect()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Real-time hand retargeting with 3D visualization'
    )
    parser.add_argument('--video', type=str, required=True,
                       help='Path to input video file')
    parser.add_argument('--urdf', type=str, required=True,
                       help='Path to Revo2 URDF file')
    parser.add_argument('--hand', type=str, default='right', 
                       choices=['right', 'left'],
                       help='Hand side (right or left)')
    
    args = parser.parse_args()
    
    # Create visualizer
    visualizer = RealtimeRetargetingVisualizer(args.urdf, args.hand)
    
    try:
        # Process video
        visualizer.process_video(args.video)
    finally:
        visualizer.close()


if __name__ == '__main__':
    main()
