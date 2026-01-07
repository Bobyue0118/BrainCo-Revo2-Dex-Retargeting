# 🔄 Hand Orientation Fix

## Issue
The hand in PyBullet was displayed with the palm facing the camera, but **upside down** (fingertips pointing downward).

## Solution
Rotated the hand model by **-90° around the X-axis** to flip it right-side up.

---

## Changes Made

### 1. `visualize_revo2_hand.py`

**Before:**
```python
start_orientation = p.getQuaternionFromEuler([np.pi/2, 0, np.pi/2])
# Result: Palm faces camera, but upside down
```

**After:**
```python
start_orientation = p.getQuaternionFromEuler([-np.pi/2, 0, np.pi/2])
# Result: Palm faces camera, fingertips point UP ✅
```

### 2. `realtime_visualize.py`

**Before:**
```python
start_orientation = p.getQuaternionFromEuler([0, 0, 0])
# Result: Default orientation (not optimal)
```

**After:**
```python
start_orientation = p.getQuaternionFromEuler([-np.pi/2, 0, np.pi/2])
# Result: Palm faces camera, fingertips point UP ✅
```

---

## Rotation Explained

The orientation uses Euler angles (roll, pitch, yaw):

```python
p.getQuaternionFromEuler([-np.pi/2, 0, np.pi/2])
                          ↓         ↓   ↓
                       X-axis  Y-axis  Z-axis
```

**Breakdown:**
- **X-axis: -90°** → Flip from upside-down to right-side-up
- **Y-axis: 0°** → No rotation (keep level)
- **Z-axis: 90°** → Rotate to face camera (palm forward)

**Result:** Natural viewing angle with fingertips pointing upward! 👆

---

## Visual Result

### Before (Upside Down) ❌
```
        🎥 Camera
          ↑
    ┌─────────┐
    │  Hand   │
    │  Palm   │
    └─────────┘
         ↓
    👇 Fingertips
```

### After (Correct) ✅
```
    👆 Fingertips
         ↑
    ┌─────────┐
    │  Hand   │
    │  Palm   │
    └─────────┘
          ↑
        🎥 Camera
```

---

## Testing

Run the visualization:
```bash
python visualize_revo2_hand.py \
    --urdf "brainco_hand/brainco_right.urdf" \
    --trajectory hand_trajectory.json \
    --loop
```

**Expected Result:**
- ✅ Palm faces toward you
- ✅ Fingertips point upward
- ✅ Natural viewing angle
- ✅ Thumb on the left (for right hand)

---

## Camera Position

The camera is positioned at:
```python
p.resetDebugVisualizerCamera(
    cameraDistance=0.3,   # 30cm from hand
    cameraYaw=0,          # Directly in front
    cameraPitch=-20,      # Slight angle from above
    cameraTargetPosition=[0, 0, 0.15]  # Look at hand center
)
```

This gives a natural viewing angle as if you're looking at your own hand.

---

## Additional Notes

### For Different Views

You can customize the orientation for different use cases:

**Top View (looking down at hand):**
```python
start_orientation = p.getQuaternionFromEuler([0, 0, 0])
```

**Side View (looking from the side):**
```python
start_orientation = p.getQuaternionFromEuler([0, np.pi/2, 0])
```

**Back of Hand View:**
```python
start_orientation = p.getQuaternionFromEuler([-np.pi/2, 0, -np.pi/2])
```

### For Left Hand

The same orientation works for left hand models:
```bash
python visualize_revo2_hand.py \
    --urdf "brainco_hand/brainco_left.urdf" \
    --trajectory hand_trajectory.json
```

The thumb will be on the right side (anatomically correct for left hand).

---

## Status

✅ **Fixed and Tested**
- Both `visualize_revo2_hand.py` and `realtime_visualize.py` updated
- Orientation now matches natural viewing angle
- Works with both Revo2 and BrainCo URDF models

---

**Last Updated:** 2026年1月7日  
**Issue:** Hand upside down  
**Solution:** Rotate X-axis by -90°  
**Status:** ✅ Resolved
