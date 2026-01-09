# 📚 BrainCo Hand Retargeting System

**Version 2.1.0** - Complete hand motion retargeting from video to robotic hand

All documentation has been moved to the `docs/` folder for better organization.

---

## 📖 Documentation Files

### Quick Start
- **[docs/README.md](docs/README.md)** - Project overview and main documentation
- **[docs/QUICKSTART.md](docs/QUICKSTART.md)** - Quick reference guide (CN/EN)

### Visualization
- **[docs/VISUALIZATION_GUIDE.md](docs/VISUALIZATION_GUIDE.md)** - PyBullet & SAPIEN guide
- **[docs/SIMULATOR_COMPARISON.md](docs/SIMULATOR_COMPARISON.md)** - PyBullet vs SAPIEN ⭐ NEW

### Technical Guides
- **[docs/README_RETARGETING.md](docs/README_RETARGETING.md)** - Complete retargeting guide
- **[docs/URDF_COMPARISON.md](docs/URDF_COMPARISON.md)** - URDF model comparison
- **[docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md)** - Step-by-step tutorial

### Project Info
- **[docs/CHANGELOG.md](docs/CHANGELOG.md)** - Version history
- **[UPDATE_NOTES.md](UPDATE_NOTES.md)** - Latest update summary

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Optional: Install SAPIEN for advanced visualization
pip install sapien

# Run video retargeting
./run_retargeting.sh

# Run image retargeting
./run_image_retargeting.sh

# Complete pipeline: images → 6-DOF control ⭐ NEW
python image_to_6dof_pipeline.py \
    --input image_frames/ \
    --urdf brainco_hand/brainco_right.urdf \
    --hand right \
    --output result/

# View in 3D (choose PyBullet, SAPIEN, or Real-time)
./run_visualization.sh
```

---

## ✨ Key Features

- 🎥 **Video Processing** - Extract hand motion from any video
- 🖼️ **Image Support** - Process single images or image sequences ⭐
- 🔄 **Complete Pipeline** - Images → 6-DOF control + rendered hand poses ⭐ NEW
- 🤖 **Smart Retargeting** - Map human joints to 11-DOF robotic hand
- 🎮 **3D Visualization** - PyBullet (fast) & SAPIEN (realistic) ⭐
- ⚡ **Real-time Mode** - See video and 3D hand together
- 📊 **Data Analysis** - Visualize trajectories and statistics
- 🔄 **Multi-URDF** - Support for Revo2 and BrainCo models
- 🤖 **6-DOF Control** - Export controllable joint commands for robot ⭐

---

## 🎮 Visualization Options

### 1. PyBullet (Fast & Interactive)
```bash
python visualize_revo2_hand.py --urdf <path> --trajectory hand_trajectory.json
```

### 2. SAPIEN (Advanced Physics & Rendering) ⭐ NEW
```bash
python visualize_sapien.py --urdf <path> --trajectory hand_trajectory.json
```

### 3. Real-time (Video + 3D)
```bash
python realtime_visualize.py --video <path> --urdf <path> --hand right
```

---

## 🤖 Supported Hand Models

This system supports **two URDF models**:

### 1. Revo2 (Original)
Location: `Revo2_URDF Description_ROS2/revo2_description/urdf/`
- `revo2_right_hand.urdf`
- `revo2_left_hand.urdf`

### 2. BrainCo Hand (New)
Location: `brainco_hand/`
- `brainco_right.urdf`
- `brainco_left.urdf`

Both models have the same 11 DOF joint structure and are compatible with all scripts.

---

## 📂 Project Structure

```
brainco/
├── docs/                        # 📚 All documentation (8 files)
│   ├── README.md                # Main documentation
│   ├── QUICKSTART.md            # Quick start guide
│   ├── VISUALIZATION_GUIDE.md   # PyBullet & SAPIEN
│   ├── SIMULATOR_COMPARISON.md  # Comparison guide ⭐
│   ├── URDF_COMPARISON.md       # URDF models
│   ├── README_RETARGETING.md    # Technical details
│   ├── DEMO_GUIDE.md            # Tutorial
│   └── CHANGELOG.md             # Version history
├── hand_retargeting.py          # Main retargeting script (video)
├── image_retargeting.py         # Image retargeting script ⭐ NEW
├── visualize_revo2_hand.py      # PyBullet 3D visualization
├── visualize_sapien.py          # SAPIEN visualization ⭐
├── realtime_visualize.py        # Real-time mode
├── visualize_trajectory.py      # 2D plotting
├── dof6_control.py              # 6-DOF control demo ⭐
├── examples.py                  # Example scripts (6 examples)
├── run_retargeting.sh           # Automated video retargeting
├── run_image_retargeting.sh     # Automated image retargeting ⭐ NEW
├── run_visualization.sh         # Automated visualization
├── requirements.txt             # Dependencies
├── Revo2_URDF Description_ROS2/ # Original Revo2 URDF
└── brainco_hand/                # New BrainCo hand URDF
    ├── brainco_right.urdf
    ├── brainco_left.urdf
    └── meshes/                  # STL mesh files
```

---

## 🎯 Usage Examples

### Video Retargeting (Original)

#### Using Revo2 URDF (Original)
```bash
python hand_retargeting.py \
    --video human_hand_video.mp4 \
    --urdf "Revo2_URDF Description_ROS2/revo2_description/urdf/revo2_right_hand.urdf" \
    --hand right
```

#### Using BrainCo Hand URDF (New)
```bash
python hand_retargeting.py \
    --video human_hand_video.mp4 \
    --urdf "brainco_hand/brainco_right.urdf" \
    --hand right
```

### Image Retargeting ⭐ NEW

#### Single Image
```bash
python image_retargeting.py \
    --image hand_photo.jpg \
    --urdf "brainco_hand/brainco_right.urdf" \
    --hand right
```

#### Image Sequence (Folder)
```bash
python image_retargeting.py \
    --folder image_frames/ \
    --pattern "*.png" \
    --fps 30 \
    --urdf "brainco_hand/brainco_right.urdf" \
    --hand right \
    --output annotated_frames/
```

#### Complete Pipeline: Images → 6-DOF + Rendered Hand ⭐ NEW
```bash
python image_to_6dof_pipeline.py \
    --input image_frames/ \
    --urdf "brainco_hand/brainco_right.urdf" \
    --hand right \
    --output result/ \
    --fps 30
```

**Output:**
- `result/annotated_images/` - Original images with landmarks
- `result/rendered_hand_poses/` - Retargeted robotic hand poses ⭐
- `result/trajectories/` - 11-DOF & 6-DOF JSON trajectories
- `result/control_commands/` - CSV control commands for robot ⭐

#### Automated Script
```bash
./run_image_retargeting.sh
```

### PyBullet Visualization
```bash
python visualize_revo2_hand.py \
    --urdf "brainco_hand/brainco_right.urdf" \
    --trajectory hand_trajectory.json \
    --loop
```

### SAPIEN Visualization ⭐ NEW
```bash
python visualize_sapien.py \
    --urdf "brainco_hand/brainco_right.urdf" \
    --trajectory hand_trajectory.json \
    --speed 1.0 \
    --loop
```

### 6-DOF Robot Control ⭐ NEW
```bash
# View 6-DOF trajectory info
python dof6_control.py hand_trajectory_6dof.json

# Export to CSV for robot control
python dof6_control.py hand_trajectory_6dof.json --export csv

# Show frame-by-frame control commands
python dof6_control.py hand_trajectory_6dof.json --show-frames
```

---

## 📊 What's New in v2.1.0

- ✨ **SAPIEN Integration** - Photo-realistic rendering & advanced physics
- 🎨 **Enhanced Visualization** - 3 modes (PyBullet, SAPIEN, Real-time)
- 🤖 **6-DOF Control Output** - Export controllable joint commands for real robots
- 📚 **Documentation Cleanup** - Removed 5 redundant files
- 📖 **New Guide** - Comprehensive simulator comparison
- 🔧 **Fixed Hand Orientation** - Palm faces camera, fingertips point upward

See **[UPDATE_NOTES.md](UPDATE_NOTES.md)** for details.

---

## 🤖 BrainCo Hand Control (6-DOF)

The BrainCo hand has **11 DOF** total, but only **6 are controllable**:

### Controllable Joints (6 DOF):
- Thumb: metacarpal + proximal (2 DOF)
- Index, Middle, Ring, Pinky: proximal each (4 DOF)

### Mimic Joints (5 DOF - auto-computed):
All distal joints automatically follow their proximal joints via URDF mimic:
- `thumb_distal` = 1.0 × `thumb_proximal`
- `index_distal` = 1.155 × `index_proximal`
- `middle_distal` = 1.155 × `middle_proximal`
- `ring_distal` = 1.155 × `ring_proximal`
- `pinky_distal` = 1.155 × `pinky_proximal`

### Output Files:
- `hand_trajectory.json` - Full 11-DOF trajectory (all joints)
- `hand_trajectory_6dof.json` - 6-DOF controllable trajectory (for robot control) ⭐

Use `dof6_control.py` to export the 6-DOF trajectory to CSV/NumPy/text format for your robot control system!

---

For complete documentation, see **[docs/README.md](docs/README.md)**
