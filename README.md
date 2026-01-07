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

# Run retargeting
./run_retargeting.sh

# View in 3D (choose PyBullet, SAPIEN, or Real-time)
./run_visualization.sh
```

---

## ✨ Key Features

- 🎥 **Video Processing** - Extract hand motion from any video
- 🤖 **Smart Retargeting** - Map human joints to 11-DOF robotic hand
- 🎮 **3D Visualization** - PyBullet (fast) & SAPIEN (realistic) ⭐
- ⚡ **Real-time Mode** - See video and 3D hand together
- 📊 **Data Analysis** - Visualize trajectories and statistics
- 🔄 **Multi-URDF** - Support for Revo2 and BrainCo models

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
├── hand_retargeting.py          # Main retargeting script
├── visualize_revo2_hand.py      # PyBullet 3D visualization
├── visualize_sapien.py          # SAPIEN visualization ⭐ NEW
├── realtime_visualize.py        # Real-time mode
├── visualize_trajectory.py      # 2D plotting
├── examples.py                  # Example scripts (5 examples)
├── run_retargeting.sh           # Automated retargeting
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

### Using Revo2 URDF (Original)
```bash
python hand_retargeting.py \
    --video human_hand_video.mp4 \
    --urdf "Revo2_URDF Description_ROS2/revo2_description/urdf/revo2_right_hand.urdf" \
    --hand right
```

### Using BrainCo Hand URDF (New)
```bash
python hand_retargeting.py \
    --video human_hand_video.mp4 \
    --urdf "brainco_hand/brainco_right.urdf" \
    --hand right
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

---

## 📊 What's New in v2.1.0

- ✨ **SAPIEN Integration** - Photo-realistic rendering & advanced physics
- 🎨 **Enhanced Visualization** - 3 modes (PyBullet, SAPIEN, Real-time)
- 📚 **Documentation Cleanup** - Removed 5 redundant files
- 📖 **New Guide** - Comprehensive simulator comparison

See **[UPDATE_NOTES.md](UPDATE_NOTES.md)** for details.

---

For complete documentation, see **[docs/README.md](docs/README.md)**
