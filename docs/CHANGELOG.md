# Changelog

All notable changes to the BrainCo Hand Retargeting System.

---

## [2.1.0] - 2026-01-07

### 🎨 New Features

#### SAPIEN Simulator Integration
- ✨ **NEW**: Added `visualize_sapien.py` for advanced physics simulation
- 🎨 Photo-realistic rendering with PBR materials
- 💡 Advanced lighting system (directional + point lights)
- ⚡ 240Hz physics simulation
- 🌍 Realistic shadows and ground plane
- 📊 Professional-quality visualization

#### Documentation Updates
- 📚 **NEW**: `SIMULATOR_COMPARISON.md` - PyBullet vs SAPIEN comparison
- 📝 Updated `VISUALIZATION_GUIDE.md` with SAPIEN instructions
- 📝 Updated `README.md` with SAPIEN features
- 🧹 Removed redundant documentation files

#### Script Enhancements
- 🔧 Updated `run_visualization.sh` with SAPIEN option (3-way menu)
- ✅ Automatic SAPIEN installation check
- 📦 Added `sapien>=2.2.0` to requirements.txt

### 📝 Files Created
- `visualize_sapien.py` - SAPIEN-based visualizer (400+ lines)
- `docs/SIMULATOR_COMPARISON.md` - Comprehensive comparison guide

### 📝 Files Removed
- `ITERATION_COMPLETE.md` - Redundant
- `UPDATE_SUMMARY.md` - Redundant
- `docs/WHATS_NEW.md` - Consolidated into CHANGELOG
- `docs/PROJECT_SUMMARY.md` - Information moved to README
- `docs/COMPLETE_OVERVIEW.md` - Redundant overview

### 🎮 Visualization Options

Now offering **3 visualization modes**:
1. **PyBullet** - Fast, interactive (default)
2. **SAPIEN** - Advanced physics & rendering (NEW!)
3. **Real-time** - Video + 3D side-by-side

---

## [2.0.0] - 2026-01-07

### 🎉 Major Updates

#### Multi-URDF Support
- ✅ Added support for BrainCo Hand URDF models
- ✅ Both Revo2 and BrainCo URDFs fully compatible with all scripts
- ✅ Interactive URDF selection in automation scripts
- ✅ Seamless switching between models

#### Documentation Reorganization
- 📁 Moved all documentation to `docs/` folder
- 📚 Created comprehensive URDF comparison guide
- 📝 Updated all documentation with new file paths
- 🔄 Added Chinese/English bilingual support in QUICKSTART

#### Testing & Verification
- ✅ Tested hand_retargeting.py with BrainCo URDF (621 frames processed)
- ✅ Tested visualize_revo2_hand.py with BrainCo URDF (11 joints detected)
- ✅ Verified mesh loading in PyBullet
- ✅ Confirmed joint naming compatibility

### 📝 Files Modified

#### Shell Scripts
- **run_retargeting.sh**: Added interactive URDF selection menu
- **run_visualization.sh**: Added interactive URDF selection menu

#### Documentation (in docs/)
- **README.md**: Added "Supported Hand Models" section
- **QUICKSTART.md**: Updated with URDF selection examples
- **URDF_COMPARISON.md**: NEW - Comprehensive comparison guide
- **CHANGELOG.md**: NEW - This file

#### Root Files
- **README.md**: Updated to reflect new documentation structure

### 🤖 Supported Models

#### Revo2 Hand
- Path: `Revo2_URDF Description_ROS2/revo2_description/urdf/`
- Files: `revo2_right_hand.urdf`, `revo2_left_hand.urdf`
- Status: ✅ Fully tested and verified

#### BrainCo Hand  
- Path: `brainco_hand/`
- Files: `brainco_right.urdf`, `brainco_left.urdf`
- Status: ✅ Tested and verified (NEW!)

### 🔧 Technical Details

Both models share:
- **11 DOF** joint structure
- Same joint naming convention: `{side}_finger_joint`
- Compatible with all Python scripts
- Compatible with automation scripts

### 📊 Test Results

**BrainCo Hand Test (2026-01-07)**
```
Video: human_hand_video.mp4
Frames: 621/621 processed (100% detection rate)
URDF: brainco_hand/brainco_right.urdf
Joints detected: 11 revolute joints
PyBullet visualization: ✅ Success
Trajectory saved: hand_trajectory.json
```

---

## [1.0.0] - 2026-01-06

### 🎉 Initial Release

#### Core Features
- ✅ MediaPipe-based hand tracking
- ✅ 11-DOF Revo2 hand retargeting
- ✅ URDF joint limit parsing
- ✅ JSON trajectory export
- ✅ Annotated video output

#### 3D Visualization
- ✅ PyBullet 3D simulation
- ✅ Trajectory replay mode
- ✅ Real-time visualization mode
- ✅ Interactive camera controls
- ✅ Playback speed control

#### Analysis Tools
- ✅ 2D trajectory plotting
- ✅ Joint angle statistics
- ✅ CSV export capability
- ✅ Custom mapping support

#### Documentation
- ✅ Main README
- ✅ Quick Start Guide
- ✅ Retargeting Guide
- ✅ Visualization Guide
- ✅ Demo Guide
- ✅ Project Summary
- ✅ What's New

#### Automation
- ✅ run_retargeting.sh
- ✅ run_visualization.sh
- ✅ examples.py with 5 examples

#### Dependencies Fixed
- ✅ MediaPipe 0.10.9 (downgraded from 0.10.31)
- ✅ protobuf 3.20.3
- ✅ PyBullet 3.2.7

---

## Upgrade Guide

### From v1.0.0 to v2.0.0

**No breaking changes!** All existing scripts and trajectory files remain compatible.

**New Features Available:**
1. Use automation scripts to select URDF model
2. Test with BrainCo Hand URDF for better visuals
3. Read URDF_COMPARISON.md for detailed comparison

**Migration Steps:**
1. Pull latest changes
2. Documentation is now in `docs/` folder
3. Run `./run_retargeting.sh` and try option 2 (BrainCo Hand)

---

## Known Issues

### v2.0.0
- None currently

### v1.0.0
- ✅ Fixed: MediaPipe v0.10.31 compatibility (downgraded to 0.10.9)

---

## Roadmap

### Future Enhancements
- [ ] Add support for custom joint mappings via config file
- [ ] Implement motion smoothing filters
- [ ] Add ROS2 integration examples
- [ ] Create web-based visualization
- [ ] Add batch processing support
- [ ] Implement multi-hand tracking
- [ ] Add gesture recognition
- [ ] Create training dataset exporter

### Documentation
- [ ] Add video tutorials
- [ ] Create troubleshooting FAQ
- [ ] Add performance benchmarks
- [ ] Create API reference

---

## Contributors

- BrainCo Team
- Community contributors welcome!

---

## License

MIT License - See LICENSE file for details

---

**For the latest updates, see the main README.md in the docs/ folder.**
