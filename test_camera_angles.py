#!/usr/bin/env python3
"""Test different camera angles to find the correct palm-facing orientation."""

import pybullet as p
import pybullet_data
import numpy as np
from PIL import Image
import os

def test_angle(yaw, pitch, hand_orientation, output_name):
    """Test a specific camera and hand orientation combination."""
    # Connect to PyBullet in DIRECT mode
    physics_client = p.connect(p.DIRECT)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    
    # Load plane
    p.loadURDF("plane.urdf", [0, 0, 0])
    
    # Load hand with specified orientation
    hand_id = p.loadURDF(
        "brainco_hand/brainco_right.urdf",
        [0, 0, 0.1],
        p.getQuaternionFromEuler(hand_orientation),
        useFixedBase=True
    )
    
    # Setup camera
    width, height = 640, 480
    view_matrix = p.computeViewMatrixFromYawPitchRoll(
        cameraTargetPosition=[0, 0, 0.1],
        distance=0.3,
        yaw=yaw,
        pitch=pitch,
        roll=0,
        upAxisIndex=2
    )
    
    proj_matrix = p.computeProjectionMatrixFOV(
        fov=60,
        aspect=width/height,
        nearVal=0.01,
        farVal=100
    )
    
    # Render
    try:
        (_, _, px, _, _) = p.getCameraImage(
            width=width,
            height=height,
            viewMatrix=view_matrix,
            projectionMatrix=proj_matrix,
            renderer=p.ER_BULLET_HARDWARE_OPENGL
        )
    except:
        (_, _, px, _, _) = p.getCameraImage(
            width=width,
            height=height,
            viewMatrix=view_matrix,
            projectionMatrix=proj_matrix,
            renderer=p.ER_TINY_RENDERER
        )
    
    # Convert to image
    rgb_array = np.reshape(px, (height, width, 4))
    rgb_array = rgb_array[:, :, :3]
    
    # Save
    img = Image.fromarray(rgb_array.astype(np.uint8))
    img.save(f"angle_test/{output_name}.jpg")
    
    # Disconnect
    p.disconnect()
    
    print(f"✓ Saved: {output_name}.jpg - Cam(yaw={yaw}, pitch={pitch}), Hand{hand_orientation}")

if __name__ == "__main__":
    # Create output directory
    os.makedirs("angle_test", exist_ok=True)
    
    print("Testing different camera and hand orientations...\n")
    
    # Test combinations
    tests = [
        # (cam_yaw, cam_pitch, hand_euler, name)
        (0, -30, [0, 0, 0], "01_yaw0_hand_default"),
        (90, -30, [0, 0, 0], "02_yaw90_hand_default"),
        (180, -30, [0, 0, 0], "03_yaw180_hand_default"),
        (270, -30, [0, 0, 0], "04_yaw270_hand_default"),
        
        (0, -30, [-np.pi/2, 0, 0], "05_yaw0_hand_pitch-90"),
        (90, -30, [-np.pi/2, 0, 0], "06_yaw90_hand_pitch-90"),
        (180, -30, [-np.pi/2, 0, 0], "07_yaw180_hand_pitch-90"),
        (270, -30, [-np.pi/2, 0, 0], "08_yaw270_hand_pitch-90"),
        
        (0, -30, [0, 0, np.pi/2], "09_yaw0_hand_roll90"),
        (90, -30, [0, 0, np.pi/2], "10_yaw90_hand_roll90"),
        (180, -30, [0, 0, np.pi/2], "11_yaw180_hand_roll90"),
        (270, -30, [0, 0, np.pi/2], "12_yaw270_hand_roll90"),
        
        (0, -30, [np.pi/2, 0, 0], "13_yaw0_hand_pitch90"),
        (90, -30, [np.pi/2, 0, 0], "14_yaw90_hand_pitch90"),
        (180, -30, [np.pi/2, 0, 0], "15_yaw180_hand_pitch90"),
        (270, -30, [np.pi/2, 0, 0], "16_yaw270_hand_pitch90"),
    ]
    
    for yaw, pitch, hand_orientation, name in tests:
        test_angle(yaw, pitch, hand_orientation, name)
    
    print(f"\n✅ All tests complete! Check the 'angle_test/' folder.")
    print("Look for the image where the palm is facing you directly.")
