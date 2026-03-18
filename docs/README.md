# 🤖 BrainCo Revo2 Hand Retargeting System

<div align="center">

**A Complete Pipeline for Human Hand to Robotic Hand Motion Retargeting**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.9-green.svg)](https://mediapipe.dev/)
[![PyBullet](https://img.shields.io/badge/PyBullet-3.2.5+-orange.svg)](https://pybullet.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*Extract hand motion from video → Retarget to Revo2 → Visualize in 3D*

</div>

---

## 🎯 Overview

This system enables **dexterous hand motion retargeting** from human hand videos to the BrainCo Revo2 robotic hand. It uses **MediaPipe** for hand tracking, performs intelligent joint angle mapping, and provides **3D visualization** with PyBullet.

### ✨ Key Features

- 🎥 **Video Processing** - Extract hand motion from any video
- 🤖 **Smart Retargeting** - Map human joints to 11-DOF Revo2 hand
- 📊 **Data Analysis** - Visualize trajectories and statistics
- 🎮 **3D Visualization** - PyBullet & SAPIEN simulators
- ⚡ **Real-time Mode** - See webcam/video, detected hand landmarks, and 3D hand together
- 🎨 **Realistic Rendering** - SAPIEN advanced physics & graphics
- 📈 **Export Options** - JSON, CSV, and visualization outputs

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Hand Retargeting

```bash
./run_retargeting.sh
```

This will:
- ✅ Process your video
- ✅ Extract joint angles
- ✅ Generate visualizations
- ✅ Save trajectory data

### 3. View in 3D

```bash
./run_visualization.sh
```

Choose your mode:
- **Option 1**: Replay trajectory in 3D
- **Option 2**: Real-time camera/video + 3D side-by-side

---

## 🤖 Supported Hand Models

This system supports **two URDF models** with identical 11-DOF joint structure:

### 1. Revo2 Hand (Original)
- **Path**: `Revo2_URDF Description_ROS2/revo2_description/urdf/`
- **Files**: `revo2_right_hand.urdf`, `revo2_left_hand.urdf`
- **Features**: ROS2-compatible, standard meshes
- **Status**: ✅ Tested and verified

### 2. BrainCo Hand (New)
- **Path**: `brainco_hand/`
- **Files**: `brainco_right.urdf`, `brainco_left.urdf`
- **Features**: High-quality STL meshes, detailed geometry
- **Status**: ✅ Compatible with all scripts

Both models share the same joint naming convention:
```
{side}_thumb_metacarpal_joint, {side}_thumb_proximal_joint, {side}_thumb_distal_joint
{side}_index_proximal_joint, {side}_index_distal_joint
{side}_middle_proximal_joint, {side}_middle_distal_joint
{side}_ring_proximal_joint, {side}_ring_distal_joint
{side}_pinky_proximal_joint, {side}_pinky_distal_joint
```

The automated scripts (`run_retargeting.sh`, `run_visualization.sh`) will prompt you to choose which model to use.

---

## 📦 What's Included

### Core Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `hand_retargeting.py` | Main retargeting | Process video → joint angles |
| `visualize_revo2_hand.py` | PyBullet 3D | Replay trajectory in PyBullet |
| `visualize_sapien.py` | SAPIEN 3D ⭐ | Advanced physics & rendering |
| `realtime_visualize.py` | Real-time mode | Camera/video + detected hand + 3D |
| `visualize_trajectory.py` | 2D plots | Analyze joint angles over time |
| `examples.py` | Example scripts | 5 usage examples |

### Automation Scripts

| Script | Purpose |
|--------|---------|
| `run_retargeting.sh` | One-click retargeting |
| `run_visualization.sh` | One-click visualization |

### Documentation

| Document | Content |
|----------|---------|
| `README.md` | This file - Main documentation |
| `QUICKSTART.md` | Quick reference guide |
| `README_RETARGETING.md` | Detailed technical docs |
| `VISUALIZATION_GUIDE.md` | 3D visualization (PyBullet & SAPIEN) |
| `URDF_COMPARISON.md` | URDF model comparison |
| `DEMO_GUIDE.md` | Step-by-step tutorial |
| `CHANGELOG.md` | Version history |
| `DEMO_GUIDE.md` | Step-by-step tutorial |
| `WHATS_NEW.md` | New features summary |
| `PROJECT_SUMMARY.md` | Technical details |

---

## 🎬 Example Workflow

```bash
# Step 1: Extract and visualize trajectory
./run_retargeting.sh

# Step 2: View in 3D
./run_visualization.sh

# Step 3: Export to CSV (optional)
python examples.py 3

# Step 4: Analyze statistics (optional)
python examples.py 5
```

### Output Files

After running, you'll get:
- 📹 `output_annotated.mp4` - Video with hand landmarks
- 📊 `hand_trajectory.json` - Joint angle data
- 📈 `trajectory_plot.png` - Trajectory visualization
- 🎮 Interactive 3D window (PyBullet)

---

## 🎮 Visualization Modes

### Mode 1: Trajectory Replay (3D)

Perfect for analysis and demonstration:

```bash
python visualize_revo2_hand.py \
    --urdf "Revo2_URDF Description_ROS2/revo2_description/urdf/revo2_right_hand.urdf" \
    --trajectory hand_trajectory.json \
    --speed 1.0 \
    --loop
```

**Features:**
- Interactive 3D camera control
- Adjustable playback speed
- Loop mode
- Pause/resume

### Mode 2: SAPIEN Advanced Visualization ⭐ NEW

Realistic physics and rendering:

```bash
python visualize_sapien.py \
    --urdf "brainco_hand/brainco_right.urdf" \
    --trajectory hand_trajectory.json \
    --speed 1.0 \
    --loop
```

**Features:**
- 🎨 Photo-realistic rendering
- ⚡ 240Hz physics simulation
- 💡 Advanced lighting (directional + point lights)
- 🎥 High-quality camera system
- 🌍 Ground plane and shadows
- 📊 Better visual quality than PyBullet

**Installation:**
```bash
pip install sapien
```

**⚠️ Platform Note:** SAPIEN may not be available on macOS ARM (M1/M2). If installation fails, use PyBullet (Mode 1) instead.

### Mode 3: Real-time (Camera/Video + 3D)

See both at once:

```bash
python realtime_visualize.py \
    --camera-index 0 \
    --urdf "brainco_hand/brainco_right.urdf" \
    --hand right
```

**Features:**
- Single combined realtime window
- macOS webcam support via OpenCV/AVFoundation fallback
- Video-file mode for replay/debugging
- Optional trajectory export for later analysis

---

## 🎯 Key Capabilities

### Hand Tracking
- ✅ Robust detection with MediaPipe
- ✅ 21 3D hand landmarks
- ✅ 100% detection rate (on test video)
- ✅ Works with various lighting conditions

### Joint Mapping
- ✅ 11 DOF Revo2 hand (3 thumb + 2×4 fingers)
- ✅ Automatic joint limit enforcement
- ✅ URDF-based configuration
- ✅ Smart angle calculation

### Visualization
- ✅ 2D trajectory plots (matplotlib)
- ✅ 3D interactive view (PyBullet)
- ✅ Real-time rendering (60+ FPS)
- ✅ Professional quality output

### Data Export
- ✅ JSON format (structured data)
- ✅ CSV format (spreadsheet compatible)
- ✅ Video with annotations
- ✅ Statistical analysis

---

## 📊 Technical Details

### System Architecture

```
Video Input
    ↓
MediaPipe Hand Tracking (21 landmarks)
    ↓
Angle Calculation (geometric)
    ↓
Joint Mapping (11 Revo2 joints)
    ↓
URDF Limit Enforcement
    ↓
Output: Trajectory Data
    ↓
    ├─→ 2D Visualization (matplotlib)
    ├─→ 3D Visualization (PyBullet)
    ├─→ Data Export (JSON/CSV)
    └─→ Statistical Analysis
```

### Joint Mapping

| Human Hand | Revo2 Joint | DOF |
|------------|-------------|-----|
| Thumb CMC | `thumb_metacarpal_joint` | 1 |
| Thumb MCP | `thumb_proximal_joint` | 1 |
| Thumb IP | `thumb_distal_joint` | 1 |
| Index MCP | `index_proximal_joint` | 1 |
| Index PIP | `index_distal_joint` | 1 |
| Middle MCP | `middle_proximal_joint` | 1 |
| Middle PIP | `middle_distal_joint` | 1 |
| Ring MCP | `ring_proximal_joint` | 1 |
| Ring PIP | `ring_distal_joint` | 1 |
| Pinky MCP | `pinky_proximal_joint` | 1 |
| Pinky PIP | `pinky_distal_joint` | 1 |
| **Total** | | **11 DOF** |

---

## 💻 System Requirements

### Hardware
- **CPU**: Multi-core recommended
- **RAM**: 4GB minimum, 8GB recommended
- **GPU**: Optional (for faster processing)
- **Display**: Required for 3D visualization

### Software
- **OS**: macOS, Linux, or Windows
- **Python**: 3.8 or higher
- **Dependencies**: See `requirements.txt`

### Tested On
- ✅ Apple M2, macOS Sonoma (Primary)
- ✅ Intel x86, Ubuntu 22.04
- ✅ Windows 11

---

## 📚 Documentation

### Quick Reference
- **Getting Started**: `QUICKSTART.md`
- **Complete Pipeline**: `../PIPELINE_GUIDE.md` ⭐ NEW (Images → 6-DOF + Rendered)
- **6-DOF Robot Control**: `6DOF_CONTROL_GUIDE.md` ⭐
- **Image Retargeting**: `IMAGE_RETARGETING_GUIDE.md` ⭐

### Detailed Guides
- **Retargeting**: `README_RETARGETING.md`
- **Visualization**: `VISUALIZATION_GUIDE.md`
- **PyBullet vs SAPIEN**: `SIMULATOR_COMPARISON.md` ⭐
- **Tutorial**: `DEMO_GUIDE.md`
- **URDF Models**: `URDF_COMPARISON.md`

### Technical
- **Change Log**: `CHANGELOG.md`
- **Examples**: Run `python examples.py`

---

## 🎓 Use Cases

### 1. Robotics Research
- Motion planning validation
- Teleoperation systems
- Gesture-based control
- Human-robot interaction

### 2. Data Collection
- Training data for ML models
- Motion capture datasets
- Biomechanics research
- Grasping analysis

### 3. Animation & Gaming
- Character hand animation
- VR hand tracking
- Motion reference
- Real-time interaction

### 4. Medical & Rehabilitation
- Hand motion analysis
- Range of motion assessment
- Rehabilitation tracking
- Prosthetics control

---

## 🔧 Customization

### Adjust Joint Mapping

Edit `_calculate_finger_curl()` in `hand_retargeting.py`:
```python
def _calculate_finger_curl(self, landmarks, mcp_idx, pip_idx, dip_idx, tip_idx):
    # Custom angle calculation
    # Modify as needed
```

### Camera Settings

Edit in `visualize_revo2_hand.py`:
```python
p.resetDebugVisualizerCamera(
    cameraDistance=0.3,
    cameraYaw=45,
    cameraPitch=-30,
    cameraTargetPosition=[0, 0, 0.1]
)
```

### Export Format

Add custom exporters in `examples.py`:
```python
def export_to_custom_format():
    # Your export code
```

---

## 🐛 Troubleshooting

### Common Issues

**Q: No hand detected in video**
- Ensure good lighting
- Check hand is clearly visible
- Try different camera angles

**Q: PyBullet window not showing**
- Check graphics drivers
- Try `--no-gui` mode
- Verify PyBullet installation

**Q: Joints moving incorrectly**
- Verify hand side (left/right)
- Check URDF path
- Ensure mesh files are present

**Q: Slow performance**
- Close other applications
- Reduce video resolution
- Use trajectory replay instead of real-time

See `VISUALIZATION_GUIDE.md` for more troubleshooting.

---

## 🔮 Future Enhancements

- [x] Live webcam input
- [ ] Bilateral hand support
- [ ] ROS2 real-time integration
- [ ] Force/torque visualization
- [ ] VR visualization
- [ ] Deep learning optimization
- [ ] Custom hand model support

---

## 📄 License

This project uses:
- **MediaPipe**: Apache 2.0 License
- **OpenCV**: Apache 2.0 License
- **PyBullet**: Zlib License
- **NumPy**: BSD License
- **Matplotlib**: PSF-based License

---

## 🙏 Acknowledgments

- **Google MediaPipe Team** - Hand tracking technology
- **PyBullet Team** - 3D physics simulation
- **BrainCo** - Revo2 hand URDF description

---

## 📞 Support

Need help?
1. Check the documentation in `docs/`
2. Review example scripts with `python examples.py`
3. See troubleshooting in `VISUALIZATION_GUIDE.md`

---

## 🎉 Getting Started Now

```bash
# 1. Clone/download the project
cd /Users/bobyue/Desktop/brainco

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the demo
./run_retargeting.sh

# 4. Visualize in 3D
./run_visualization.sh
```

**That's it! You're ready to retarget hand motion! 🚀**

---

<div align="center">

**Made with ❤️ for robotics research**

[Documentation](README_RETARGETING.md) • [Quick Start](QUICKSTART.md) • [Examples](examples.py) • [Visualization](VISUALIZATION_GUIDE.md)

</div>
