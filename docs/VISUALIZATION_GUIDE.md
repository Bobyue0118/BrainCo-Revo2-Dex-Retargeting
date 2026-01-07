# BrainCo Revo2 Hand 3D Visualization Guide

## 📋 Overview

This guide covers the 3D visualization tools for BrainCo Revo2 hand retargeting. You can visualize the retargeted hand motion in three ways:

1. **PyBullet Replay** - Fast, interactive trajectory replay
2. **SAPIEN Visualization** ⭐ NEW - Advanced physics & realistic rendering
3. **Real-time Visualization** - See both video and 3D hand side-by-side

## 🚀 Quick Start

### Option 1: Automated Script (Recommended)

```bash
./run_visualization.sh
```

This script will guide you through:
- Choosing URDF model (Revo2 or BrainCo)
- Choosing visualization mode
- Checking for required files
- Running the appropriate visualization

### Option 2: Manual Commands

#### A. PyBullet Replay (Fast & Interactive)

```bash
python visualize_revo2_hand.py \
    --urdf "Revo2_URDF Description_ROS2/revo2_description/urdf/revo2_right_hand.urdf" \
    --trajectory hand_trajectory.json \
    --speed 1.0 \
    --loop
```

**Parameters:**
- `--urdf`: Path to URDF file
- `--trajectory`: Path to trajectory JSON file
- `--speed`: Playback speed (1.0 = normal, 2.0 = 2x faster)
- `--loop`: Loop the animation indefinitely

#### B. SAPIEN Visualization ⭐ NEW (Advanced Physics & Rendering)

```bash
python visualize_sapien.py \
    --urdf "brainco_hand/brainco_right.urdf" \
    --trajectory hand_trajectory.json \
    --speed 1.0 \
    --loop
```

**Parameters:**
- `--urdf`: Path to URDF file
- `--trajectory`: Path to trajectory JSON file  
- `--speed`: Playback speed multiplier
- `--loop`: Loop the animation
- `--headless`: Run without GUI (for batch processing)

**Installation:**
```bash
pip install sapien
```

**⚠️ Platform Support:**
- ✅ **Linux (x86_64)** - Fully supported
- ✅ **Windows (x86_64)** - Fully supported
- ⚠️ **macOS (ARM M1/M2)** - Not yet supported
- ⚠️ **macOS (Intel)** - Limited support

**If SAPIEN is not available on your platform**, use PyBullet instead (see section A above).

**Advantages over PyBullet:**
- 🎨 Photo-realistic rendering
- 💡 Advanced lighting system
- ⚡ 240Hz physics simulation
- 🌍 Better shadows and ground plane
- 📊 Higher visual quality

#### C. Real-time Video + 3D

```bash
python realtime_visualize.py \
    --video human_hand_video.mp4 \
    --urdf "Revo2_URDF Description_ROS2/revo2_description/urdf/revo2_right_hand.urdf" \
    --hand right
```

**Parameters:**
- `--video`: Path to input video
- `--urdf`: Path to URDF file
- `--hand`: Hand side (right or left)

## 🎮 Controls

### During Playback:

| Key | Action |
|-----|--------|
| `SPACE` | Pause/Resume |
| `q` | Quit |

### Mouse (PyBullet Window):

- **Left Click + Drag**: Rotate camera
- **Right Click + Drag**: Pan camera
- **Scroll Wheel**: Zoom in/out

## 📦 Features

### 1. Trajectory Replay (`visualize_revo2_hand.py`)

**What it does:**
- Loads pre-recorded trajectory from JSON
- Displays 3D Revo2 hand in PyBullet
- Animates hand according to recorded motion
- Supports looping and speed control

**Use cases:**
- Analyzing hand motion in detail
- Adjusting camera angles for best view
- Creating demonstration videos
- Debugging joint movements

**Example:**
```bash
# Play at half speed with looping
python visualize_revo2_hand.py \
    --urdf "Revo2_URDF Description_ROS2/revo2_description/urdf/revo2_right_hand.urdf" \
    --trajectory hand_trajectory.json \
    --speed 0.5 \
    --loop
```

### 2. Real-time Visualization (`realtime_visualize.py`)

**What it does:**
- Processes video frame-by-frame
- Detects hand with MediaPipe
- Updates 3D hand in real-time
- Shows both video and 3D side-by-side

**Use cases:**
- Live demonstration
- Real-time debugging
- Comparing source and target
- Interactive exploration

**Example:**
```bash
# Process with left hand
python realtime_visualize.py \
    --video my_left_hand.mp4 \
    --urdf "Revo2_URDF Description_ROS2/revo2_description/urdf/revo2_left_hand.urdf" \
    --hand left
```

## 🛠️ Workflow

### Complete Pipeline

```bash
# Step 1: Record trajectory from video
python hand_retargeting.py \
    --video human_hand_video.mp4 \
    --urdf "Revo2_URDF Description_ROS2/revo2_description/urdf/revo2_right_hand.urdf" \
    --hand right \
    --output annotated.mp4

# Step 2: Visualize trajectory in 3D
python visualize_revo2_hand.py \
    --urdf "Revo2_URDF Description_ROS2/revo2_description/urdf/revo2_right_hand.urdf" \
    --trajectory hand_trajectory.json \
    --loop

# Step 3: Analyze trajectory
python visualize_trajectory.py --trajectory hand_trajectory.json
```

## 📊 Output

### PyBullet Window
- 3D rendered Revo2 hand
- Realistic physics simulation
- Interactive camera control
- Real-time joint updates

### Terminal Output
```
============================================================
BrainCo Revo2 Hand 3D Visualizer
============================================================

✓ Loaded Revo2 hand from: .../revo2_right_hand.urdf
Total joints in URDF: 25
  Joint 0: right_thumb_metacarpal_joint (Revolute)
  Joint 1: right_thumb_proximal_joint (Revolute)
  ...
✓ Found 11 controllable joints

============================================================
Visualizing Trajectory
============================================================
File: hand_trajectory.json
Total frames: 621
FPS: 30
Playback speed: 1.0x
Loop: True
============================================================

Frame 1/621 | Time: 0.00s | Hand: ✓
```

## 🎨 Customization

### Camera Settings

Edit the camera in the script:
```python
p.resetDebugVisualizerCamera(
    cameraDistance=0.3,    # Distance from target
    cameraYaw=45,          # Horizontal rotation
    cameraPitch=-30,       # Vertical angle
    cameraTargetPosition=[0, 0, 0.1]  # Look at point
)
```

### Joint Colors

Modify PyBullet visual settings:
```python
# Change link color
p.changeVisualShape(
    hand_id,
    linkIndex=i,
    rgbaColor=[1, 0, 0, 1]  # Red
)
```

### Background

Change simulation environment:
```python
# Load different ground
p.loadURDF("plane.urdf")  # Default
p.loadURDF("table/table.urdf")  # Table
```

## 🔧 Troubleshooting

### Issue: "Cannot open URDF file"

**Solution:**
- Check URDF path is correct
- Use absolute path or correct relative path
- Ensure all mesh files (.STL) are in the correct location

### Issue: "PyBullet window not appearing"

**Solution:**
```bash
# Check if PyBullet is installed
python -c "import pybullet; print('OK')"

# Reinstall if needed
pip install --upgrade pybullet
```

### Issue: "Joints not moving"

**Solution:**
- Verify trajectory file has joint_angles data
- Check joint names match URDF
- Ensure angles are in correct units (radians)

### Issue: "Video and 3D out of sync"

**Solution:**
- This can happen with slow systems
- Try reducing video resolution
- Close other applications
- Use trajectory replay instead

## 📈 Performance Tips

1. **For Smooth Playback:**
   - Close unnecessary applications
   - Use lower video resolution
   - Reduce playback speed if needed

2. **For Recording:**
   - Use screen recording software
   - Set loop=True for continuous recording
   - Adjust camera before recording

3. **For Best Quality:**
   - Use high-quality input video
   - Ensure good hand detection (100% detection rate)
   - Use slower playback for detailed analysis

## 🎥 Creating Videos

### Record 3D Visualization

1. Start visualization:
```bash
python visualize_revo2_hand.py \
    --urdf "..." \
    --trajectory hand_trajectory.json \
    --loop
```

2. Use screen recording:
   - **macOS**: Cmd+Shift+5
   - **Windows**: Win+G
   - **Linux**: OBS Studio, SimpleScreenRecorder

3. Adjust camera angle before recording

## 🔗 Integration with ROS2

The visualizer can be adapted for ROS2:

```python
# Subscribe to joint states
from sensor_msgs.msg import JointState

def joint_state_callback(msg):
    joint_angles = dict(zip(msg.name, msg.position))
    visualizer.set_joint_angles(joint_angles)

# In ROS2 node
self.subscription = self.create_subscription(
    JointState,
    '/revo2/joint_states',
    joint_state_callback,
    10
)
```

## 📚 Additional Resources

- **PyBullet Documentation**: https://pybullet.org/
- **MediaPipe Hands**: https://google.github.io/mediapipe/solutions/hands
- **URDF Spec**: http://wiki.ros.org/urdf/XML

## 💡 Tips

1. **Best viewing angle**: Yaw=45°, Pitch=-30°, Distance=0.3m
2. **Recording**: Use loop mode and adjust speed as needed
3. **Analysis**: Pause frequently to examine poses
4. **Comparison**: Use real-time mode to compare source and target

---

**Happy Visualizing!** 🎉
