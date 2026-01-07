# Human Hand to BrainCo Revo2 Hand Retargeting

This project provides Python scripts for retargeting human hand motion from video to the BrainCo Revo2 robotic hand.

## Features

- **Hand Tracking**: Uses MediaPipe for robust hand landmark detection from video
- **Motion Retargeting**: Maps human hand joint angles to Revo2 robotic hand joints
- **Joint Limit Enforcement**: Respects URDF-defined joint limits
- **Trajectory Recording**: Saves joint angle trajectories to JSON format
- **Visualization**: Plots joint angles over time for analysis
- **Real-time Display**: Shows hand tracking and joint angles during processing

## Requirements

- Python 3.8 or higher
- OpenCV
- MediaPipe
- NumPy
- Matplotlib (for visualization)

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

For visualization, also install matplotlib:
```bash
pip install matplotlib
```

## Usage

### 1. Process Hand Video

Run the retargeting script on your video:

```bash
python hand_retargeting.py \
    --video human_hand_video.mp4 \
    --urdf "Revo2_URDF Description_ROS2/revo2_description/urdf/revo2_right_hand.urdf" \
    --hand right \
    --output output_video.mp4
```

**Parameters:**
- `--video`: Path to input video file
- `--urdf`: Path to Revo2 URDF file
- `--hand`: Hand side (`right` or `left`)
- `--output`: (Optional) Path to save annotated output video
- `--no-save-trajectory`: (Optional) Skip saving trajectory JSON file

### 2. Visualize Trajectory

After processing, visualize the extracted joint trajectories:

```bash
python visualize_trajectory.py \
    --trajectory hand_trajectory.json \
    --output trajectory_plot.png
```

**Parameters:**
- `--trajectory`: Path to trajectory JSON file
- `--output`: (Optional) Path to save plot image
- `--stats-only`: (Optional) Only print statistics without plotting

### 3. Quick Start Example

```bash
# Process the video
python hand_retargeting.py \
    --video human_hand_video.mp4 \
    --urdf "Revo2_URDF Description_ROS2/revo2_description/urdf/revo2_right_hand.urdf" \
    --hand right \
    --output annotated_video.mp4

# Visualize results
python visualize_trajectory.py --trajectory hand_trajectory.json
```

## Output Files

1. **hand_trajectory.json**: Contains frame-by-frame joint angles
   - Frame number and timestamp
   - Joint angles in degrees for all Revo2 joints
   
2. **annotated_video.mp4**: Video with hand landmarks and joint angles overlay

3. **trajectory_plot.png**: Visualization of joint angles over time

## Revo2 Hand Joint Mapping

The script maps human hand landmarks to the following Revo2 joints:

### Thumb (3 DOF)
- `thumb_metacarpal_joint`: CMC joint (abduction/adduction)
- `thumb_proximal_joint`: MCP joint (flexion/extension)
- `thumb_distal_joint`: IP joint (flexion/extension)

### Index Finger (2 DOF)
- `index_proximal_joint`: MCP joint
- `index_distal_joint`: PIP joint

### Middle Finger (2 DOF)
- `middle_proximal_joint`: MCP joint
- `middle_distal_joint`: PIP joint

### Ring Finger (2 DOF)
- `ring_proximal_joint`: MCP joint
- `ring_distal_joint`: PIP joint

### Pinky Finger (2 DOF)
- `pinky_proximal_joint`: MCP joint
- `pinky_distal_joint`: PIP joint

**Total: 11 DOF**

## Technical Details

### Hand Tracking
- Uses Google MediaPipe Hands for 21 3D hand landmarks
- Processes video at original frame rate
- Handles occlusions and varying lighting conditions

### Retargeting Algorithm
1. Extract 3D hand landmarks from video frames
2. Calculate joint angles from landmark positions
3. Map human joint angles to Revo2 joint space
4. Apply URDF joint limits
5. Output joint commands in radians/degrees

### Joint Angle Calculation
- **Finger flexion**: Calculated from 3-point angle between MCP-PIP-DIP
- **Thumb abduction**: Calculated from CMC joint orientation
- **All angles**: Clamped to URDF-specified joint limits

## Troubleshooting

### No hand detected
- Ensure good lighting in the video
- Make sure the hand is clearly visible
- Try adjusting MediaPipe confidence thresholds in the code

### Video processing is slow
- MediaPipe can be CPU-intensive
- Consider downsampling the video first
- Process shorter clips for testing

### Joint angles look wrong
- Verify the correct hand side (left/right) is specified
- Check that the URDF file path is correct
- Ensure the video shows the hand from a reasonable angle

## Integration with ROS2

The output trajectory can be used with ROS2:

```python
# Example: Publishing to ROS2 joint trajectory controller
import json
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

with open('hand_trajectory.json', 'r') as f:
    trajectory = json.load(f)

traj_msg = JointTrajectory()
# ... populate with joint names and trajectory points
```

## Customization

### Adjust MediaPipe Settings
Edit `hand_retargeting.py`, line ~250:
```python
with self.mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,  # Adjust this
    min_tracking_confidence=0.5    # Adjust this
) as hands:
```

### Modify Joint Mapping
Edit the `retarget_hand_pose()` method to customize the angle mapping logic.

## License

This project uses:
- MediaPipe (Apache 2.0)
- OpenCV (Apache 2.0)
- BrainCo Revo2 URDF (check original license)

## Acknowledgments

- Google MediaPipe team for hand tracking
- BrainCo for Revo2 hand URDF description

## Contact

For questions or issues, please open an issue on the project repository.
