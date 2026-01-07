# 🤖 URDF Model Comparison Guide

## Overview

This document compares the two supported URDF models for the BrainCo hand retargeting system.

---

## Supported Models

### 1. Revo2 Hand (Original)
**Location**: `Revo2_URDF Description_ROS2/revo2_description/urdf/`

**Files**:
- `revo2_right_hand.urdf`
- `revo2_left_hand.urdf`

**Features**:
- ✅ ROS2-compatible structure
- ✅ Standard STL meshes
- ✅ Tested and verified with all scripts
- ✅ Includes launch files for RViz visualization
- ✅ Documentation in Chinese and English

**Mesh Files**: Located in `Revo2_URDF Description_ROS2/revo2_description/meshes/`

---

### 2. BrainCo Hand (New)
**Location**: `brainco_hand/`

**Files**:
- `brainco_right.urdf`
- `brainco_left.urdf`
- `brainco.yml` (configuration file)

**Features**:
- ✅ High-quality detailed STL meshes
- ✅ Improved geometry and visual appearance
- ✅ Compatible with all Python scripts
- ✅ Same 11-DOF joint structure as Revo2
- ✅ Ready for PyBullet visualization

**Mesh Files**: Located in `brainco_hand/meshes/` (34 STL files)

---

## Joint Structure Comparison

Both models share the **exact same joint naming convention** and DOF structure:

### Right Hand Joints (11 DOF)

| Finger | Joint Name | Type | Description |
|--------|-----------|------|-------------|
| **Thumb** | `right_thumb_metacarpal_joint` | Revolute | CMC joint |
| | `right_thumb_proximal_joint` | Revolute | MCP joint |
| | `right_thumb_distal_joint` | Revolute | IP joint |
| **Index** | `right_index_proximal_joint` | Revolute | MCP joint |
| | `right_index_distal_joint` | Revolute | PIP joint |
| **Middle** | `right_middle_proximal_joint` | Revolute | MCP joint |
| | `right_middle_distal_joint` | Revolute | PIP joint |
| **Ring** | `right_ring_proximal_joint` | Revolute | MCP joint |
| | `right_ring_distal_joint` | Revolute | PIP joint |
| **Pinky** | `right_pinky_proximal_joint` | Revolute | MCP joint |
| | `right_pinky_distal_joint` | Revolute | PIP joint |

### Left Hand Joints (11 DOF)

Replace `right_` with `left_` in all joint names above.

---

## Compatibility Matrix

| Feature | Revo2 Hand | BrainCo Hand |
|---------|-----------|--------------|
| **hand_retargeting.py** | ✅ | ✅ |
| **visualize_revo2_hand.py** | ✅ | ✅ |
| **realtime_visualize.py** | ✅ | ✅ |
| **visualize_trajectory.py** | ✅ | ✅ |
| **examples.py** | ✅ | ✅ |
| **run_retargeting.sh** | ✅ | ✅ |
| **run_visualization.sh** | ✅ | ✅ |
| **ROS2/RViz** | ✅ | ⚠️ (needs testing) |
| **PyBullet 3D** | ✅ | ✅ |

---

## Usage Examples

### Using Revo2 Hand

```bash
# Automated (with menu selection)
./run_retargeting.sh
# Choose option 1

# Manual command
python hand_retargeting.py \
    --video human_hand_video.mp4 \
    --urdf "Revo2_URDF Description_ROS2/revo2_description/urdf/revo2_right_hand.urdf" \
    --hand right
```

### Using BrainCo Hand

```bash
# Automated (with menu selection)
./run_retargeting.sh
# Choose option 2

# Manual command
python hand_retargeting.py \
    --video human_hand_video.mp4 \
    --urdf "brainco_hand/brainco_right.urdf" \
    --hand right
```

---

## Visualization Comparison

### Revo2 Hand
- Standard industrial appearance
- Lighter mesh files (~50KB per STL)
- Faster loading times
- Good for performance-critical applications

### BrainCo Hand
- Detailed, realistic appearance
- Larger mesh files (~100-200KB per STL)
- Slightly longer loading times
- Better for demonstrations and presentations

---

## Technical Specifications

### File Sizes

| Model | URDF Size | Mesh Count | Total Mesh Size |
|-------|-----------|------------|-----------------|
| Revo2 | ~45 KB | 17 files | ~850 KB |
| BrainCo | ~22 KB | 34 files | ~4 MB |

### Joint Limits

Both models have similar joint limits:

```yaml
Thumb Metacarpal: [-0.5, 0.5] rad
Thumb Proximal: [-0.2, 1.2] rad
Thumb Distal: [0, 1.5] rad

Index/Middle/Ring/Pinky Proximal: [-0.2, 1.5] rad
Index/Middle/Ring/Pinky Distal: [0, 1.5] rad
```

*Note: Exact limits may vary slightly between models.*

---

## Choosing the Right Model

### Use Revo2 Hand if:
- ✅ You need ROS2 integration
- ✅ Performance is critical
- ✅ You want faster loading times
- ✅ You're working with the original BrainCo documentation

### Use BrainCo Hand if:
- ✅ You want better visual quality
- ✅ You're creating demos or presentations
- ✅ You need detailed mesh geometry
- ✅ Visual appearance matters more than performance

---

## Migration Guide

Switching between models is seamless:

1. **Using Automation Scripts**:
   - Simply choose a different option when prompted
   - No code changes needed

2. **Using Python Scripts**:
   - Change the `--urdf` parameter only
   - All other parameters remain the same

3. **Trajectory Files**:
   - JSON trajectory files are compatible with both models
   - No conversion needed

### Example Migration

```bash
# From Revo2
python visualize_revo2_hand.py \
    --urdf "Revo2_URDF Description_ROS2/revo2_description/urdf/revo2_right_hand.urdf" \
    --trajectory hand_trajectory.json

# To BrainCo (just change URDF path)
python visualize_revo2_hand.py \
    --urdf "brainco_hand/brainco_right.urdf" \
    --trajectory hand_trajectory.json
```

---

## Testing Both Models

To test both models with the same video:

```bash
# Test Revo2
python hand_retargeting.py \
    --video human_hand_video.mp4 \
    --urdf "Revo2_URDF Description_ROS2/revo2_description/urdf/revo2_right_hand.urdf" \
    --hand right \
    --output output_revo2.mp4

mv hand_trajectory.json trajectory_revo2.json

# Test BrainCo
python hand_retargeting.py \
    --video human_hand_video.mp4 \
    --urdf "brainco_hand/brainco_right.urdf" \
    --hand right \
    --output output_brainco.mp4

mv hand_trajectory.json trajectory_brainco.json

# Compare results
diff trajectory_revo2.json trajectory_brainco.json
```

---

## Troubleshooting

### Issue: "URDF file not found"
**Solution**: Check that you're using the correct relative path from the project root.

### Issue: "Mesh files not loading in PyBullet"
**Solution**: 
- Ensure mesh files are in the correct directory
- For BrainCo: Check `brainco_hand/meshes/`
- For Revo2: Check `Revo2_URDF Description_ROS2/revo2_description/meshes/`

### Issue: "Joint not found"
**Solution**: 
- Verify you're using the correct `--hand` parameter (right/left)
- Check that joint names in URDF match expected format

---

## Future Compatibility

Both URDF models follow standard robotics conventions and should remain compatible with:
- Future versions of PyBullet
- ROS2 updates
- MoveIt2 integration
- Custom simulation environments

---

## Additional Resources

- **Revo2 Documentation**: `Revo2_URDF Description_ROS2/revo2_description/README.md`
- **BrainCo Config**: `brainco_hand/brainco.yml`
- **Visualization Guide**: `docs/VISUALIZATION_GUIDE.md`
- **Main Documentation**: `docs/README.md`

---

**Last Updated**: 2026年1月7日
