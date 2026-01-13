# Hand Side Detection Fix - Summary

## Problem

When running the pipeline with `--hand right`, the system was detecting **left hands** in annotated images, while rendered poses showed right hands. This was reversed for `--hand left`.

## Root Cause

MediaPipe returns hand labels from the **camera's perspective**, which is **mirrored** from the actual hand side:

- MediaPipe "Left" = actual **RIGHT hand**
- MediaPipe "Right" = actual **LEFT hand**

The previous code was directly matching MediaPipe's label with the user's request, causing the wrong hand to be detected.

## Solution

Added label flipping logic in all detection functions:

```python
# OLD (WRONG)
if detected_label.lower() == self.hand_side:
    target_hand_idx = idx

# NEW (CORRECT)
if detected_label == 'left' and self.hand_side == 'right':
    target_hand_idx = idx
elif detected_label == 'right' and self.hand_side == 'left':
    target_hand_idx = idx
```

## Files Modified

1. **`image_retargeting.py`** (3 locations)
   - `process_single_image()` - Line ~72
   - `process_image_sequence()` - Line ~223
   - `process_image_list()` - Line ~355

2. **`hand_retargeting.py`** (1 location)
   - `process_video()` - Line ~343

3. **`USAGE.md`**
   - Updated documentation to explain the label flipping

## Verification

Now when you run:

```bash
python image_to_6dof_pipeline.py \
    --input tray \
    --urdf brainco_hand/brainco_right.urdf \
    --hand right \
    --output result/
```

**Expected behavior:**
- ✅ Annotated images show **RIGHT hands** only
- ✅ Rendered poses show **RIGHT hands** 
- ✅ Both are consistent and correct

Similarly for `--hand left`:
- ✅ Annotated images show **LEFT hands** only
- ✅ Rendered poses show **LEFT hands**
- ✅ Both are consistent and correct

## Testing

You can verify the fix by:

1. Running the pipeline on images with both hands visible
2. Checking that only the specified hand side is detected
3. Verifying annotated images match rendered poses

Test command:
```bash
python test_hand_detection.py tray/23.png
```

This will show MediaPipe's label vs. the actual hand side.
