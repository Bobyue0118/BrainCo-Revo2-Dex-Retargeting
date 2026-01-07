# ⚠️  SAPIEN Platform Compatibility Note

## Issue
SAPIEN installation failed on macOS (ARM M1/M2):
```bash
pip install sapien
ERROR: Could not find a version that satisfies the requirement sapien
```

## Root Cause
SAPIEN is primarily built for Linux (x86_64) and Windows (x86_64) platforms. 
**macOS ARM (M1/M2) is not currently supported.**

---

## ✅ Solution: Use PyBullet

PyBullet is fully functional and works on **all platforms** including macOS ARM.

### Quick Command
```bash
# Instead of SAPIEN, use PyBullet:
python visualize_revo2_hand.py \
    --urdf "brainco_hand/brainco_right.urdf" \
    --trajectory hand_trajectory.json \
    --speed 1.0 \
    --loop
```

---

## 🎮 Updated Visualization Options

### 1. PyBullet (Recommended for macOS) ✅
```bash
./run_visualization.sh
# Select option 1
```

**Advantages:**
- ✅ Works on all platforms (macOS ARM/Intel, Linux, Windows)
- ⚡ Fast rendering (~60 FPS)
- 🎮 Interactive camera control
- 📦 Easy installation
- 🔧 Well documented

### 2. SAPIEN (Linux/Windows only) ⚠️
```bash
# Only works on Linux/Windows
pip install sapien
python visualize_sapien.py --urdf <path> --trajectory <path>
```

**Advantages:**
- 🎨 Photo-realistic rendering
- 💡 Advanced PBR lighting
- 🌍 Better shadows
- **⚠️  Not available on macOS ARM**

### 3. Real-time Mode ✅
```bash
./run_visualization.sh
# Select option 3
```

**Works on all platforms**

---

## 📋 Platform Support Matrix

| Platform | PyBullet | SAPIEN | Recommendation |
|----------|----------|--------|----------------|
| macOS ARM (M1/M2) | ✅ | ❌ | Use PyBullet |
| macOS Intel | ✅ | ⚠️  | Use PyBullet |
| Linux x86_64 | ✅ | ✅ | Either (SAPIEN for quality) |
| Windows x86_64 | ✅ | ✅ | Either (SAPIEN for quality) |

---

## 🔧 Code Changes Made

### 1. Updated `requirements.txt`
```
# Commented out SAPIEN with platform notes
# sapien>=2.2.0  # Optional - not available on macOS ARM
```

### 2. Updated `visualize_sapien.py`
- Added platform detection and helpful error messages
- Graceful fallback suggestions to PyBullet
- Type hints fixed for optional SAPIEN import

### 3. Updated `run_visualization.sh`
- Enhanced SAPIEN installation check
- Offers to fall back to PyBullet if SAPIEN unavailable
- Better error handling

### 4. Updated Documentation
- `docs/README.md` - Added platform warning
- `docs/VISUALIZATION_GUIDE.md` - Added platform support section
- `docs/SIMULATOR_COMPARISON.md` - Added platform compatibility matrix

---

## 💡 Recommendations

### For macOS Users (You!)
**Use PyBullet for all visualization needs.**

PyBullet provides:
- ✅ Excellent 3D visualization
- ✅ Physics simulation
- ✅ Interactive camera
- ✅ All features you need
- ✅ Actually works on your system!

### For Linux/Windows Users
**Can choose between PyBullet and SAPIEN based on needs:**
- Development/Testing → PyBullet (faster)
- Presentations/Publications → SAPIEN (prettier)

---

## 🚀 Next Steps

### Immediate Action
Use PyBullet for visualization:
```bash
# Process video
./run_retargeting.sh

# Visualize (choose option 1: PyBullet)
./run_visualization.sh
```

### Future Options
If you need SAPIEN-quality rendering:
1. **Use Linux VM or Docker**
2. **Remote server** with Linux
3. **Wait for macOS ARM support** (check https://sapien.ucsd.edu/)

---

## 📊 Summary

| Aspect | Status |
|--------|--------|
| **Issue** | SAPIEN not available on macOS ARM |
| **Solution** | Use PyBullet (fully functional) |
| **Impact** | None - PyBullet covers all needs |
| **Code Status** | ✅ Updated with graceful fallbacks |
| **Documentation** | ✅ Updated with platform notes |
| **System Status** | ✅ Fully operational with PyBullet |

---

## ✅ What Works

**Everything works perfectly with PyBullet!**

- ✅ Hand tracking (MediaPipe)
- ✅ 11-DOF retargeting
- ✅ 3D visualization (PyBullet)
- ✅ Real-time mode
- ✅ Multi-URDF support
- ✅ All documentation
- ✅ Automated scripts

**SAPIEN is just an optional enhancement for Linux/Windows users.**

---

**Status**: ✅ Fully Operational  
**Recommended**: Use PyBullet  
**Last Updated**: 2026年1月7日
