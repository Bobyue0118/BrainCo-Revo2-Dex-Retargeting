# Quick Usage Guide

## 🚀 One-Command Image to 6-DOF Control

### Single Image → 6-DOF Joint Angles
```bash
python image_retargeting.py \
    --image YOUR_IMAGE.jpg \
    --urdf brainco_hand/brainco_right.urdf \
    --hand right
```

**Output:** `single_image_result.json` containing 6-DOF joint angles

---

### Image Sequence → Complete Pipeline (Recommended)
```bash
python image_to_6dof_pipeline.py \
    --input YOUR_IMAGES_FOLDER/ \
    --urdf brainco_hand/brainco_right.urdf \
    --hand right \
    --output result/
```

**Output Structure:**
```
result/
├── trajectories/
│   └── hand_trajectory_6dof.json    ← 6-DOF control commands
├── control_commands/
│   └── control_trajectory_6dof.csv  ← CSV format (frame, joint1, joint2, ...)
├── rendered_hand_poses/              ← 3D visualization (palm facing front)
│   └── hand_pose_*.jpg
└── annotated_images/                 ← MediaPipe landmarks
    └── annotated_*.jpg
```

---

## 📊 6-DOF Joint Angles Output Format

### JSON Format (`hand_trajectory_6dof.json`)
```json
{
  "fps": 30.0,
  "angle_unit": "degrees",
  "dof": 6,
  "controllable_joints": [
    "right_thumb_metacarpal_joint",
    "right_thumb_proximal_joint",
    "right_index_proximal_joint",
    "right_middle_proximal_joint",
    "right_ring_proximal_joint",
    "right_pinky_proximal_joint"
  ],
  "frames": [
    {
      "right_thumb_metacarpal_joint": 75.49,
      "right_thumb_proximal_joint": 6.27,
      "right_index_proximal_joint": 4.10,
      "right_middle_proximal_joint": 5.44,
      "right_ring_proximal_joint": 4.62,
      "right_pinky_proximal_joint": 3.86
    }
  ]
}
```

### CSV Format (`control_trajectory_6dof.csv`)
```csv
frame,right_thumb_metacarpal_joint,right_thumb_proximal_joint,right_index_proximal_joint,right_middle_proximal_joint,right_ring_proximal_joint,right_pinky_proximal_joint
0,75.49,6.27,4.10,5.44,4.62,3.86
1,61.74,46.09,2.86,3.34,6.81,2.94
```

**All angles are in degrees** for easy reading.

---

## 🎯 Real-World Examples

### Example 1: Process Single Hand Image
```bash
python image_retargeting.py \
    --image hand_photo.jpg \
    --urdf brainco_hand/brainco_right.urdf \
    --hand right
```
Output: `single_image_result.json` with 6-DOF angles

---

### Example 2: Process Video Frames (Best Quality)
```bash
# Step 1: Extract frames from video
mkdir frames
ffmpeg -i human_hand_video.mp4 -vf fps=10 frames/frame_%04d.jpg

# Step 2: Run complete pipeline
python image_to_6dof_pipeline.py \
    --input frames/ \
    --urdf brainco_hand/brainco_right.urdf \
    --hand right \
    --output robot_control/ \
    --fps 10
```
Output: Complete control data + visualizations in `robot_control/`

---

### Example 3: Process Specific Images
```bash
python image_retargeting.py \
    --list img1.jpg img2.jpg img3.jpg \
    --urdf brainco_hand/brainco_right.urdf \
    --hand right \
    --output my_results/
```

---

## 🤖 Use in Robot Control System

### Python
```python
import json

# Load 6-DOF trajectory
with open('result/trajectories/hand_trajectory_6dof.json') as f:
    trajectory = json.load(f)

# Send to robot (angles are in degrees)
for frame in trajectory['frames']:
    robot.set_joint_angles({
        'thumb_base': frame['right_thumb_metacarpal_joint'],
        'thumb_proximal': frame['right_thumb_proximal_joint'],
        'index': frame['right_index_proximal_joint'],
        'middle': frame['right_middle_proximal_joint'],
        'ring': frame['right_ring_proximal_joint'],
        'pinky': frame['right_pinky_proximal_joint']
    })
    time.sleep(1.0 / trajectory['fps'])
```

### Read from CSV
```python
import pandas as pd

df = pd.read_csv('result/control_commands/control_trajectory_6dof.csv')
for _, row in df.iterrows():
    robot.set_joint_angles(row[1:].to_dict())  # Skip frame column
```

---

## 🔧 Advanced Options

### Custom Resolution for Rendered Images
```bash
python image_to_6dof_pipeline.py \
    --input frames/ \
    --urdf brainco_hand/brainco_right.urdf \
    --hand right \
    --output result/ \
    --width 1280 \
    --height 720
```

### Skip Rendering (Faster)
```bash
python image_to_6dof_pipeline.py \
    --input frames/ \
    --urdf brainco_hand/brainco_right.urdf \
    --hand right \
    --output result/ \
    --skip-render
```

### Process Left Hand
```bash
python image_to_6dof_pipeline.py \
    --input frames/ \
    --urdf brainco_hand/brainco_left.urdf \
    --hand left \
    --output result/
```

---

## 📝 Notes

- **Angle Unit**: All outputs use **degrees** (human-readable)
- **Detection**: MediaPipe detects hand landmarks automatically
- **Rendering**: Hand palm faces **forward** (toward camera) in 3D visualizations
- **Frame Rate**: Default 30 FPS, adjustable with `--fps` option
- **Image Formats**: Supports `.jpg`, `.jpeg`, `.png`, `.JPG`, `.PNG`

---

## 📚 Full Documentation

For more details, see:
- `docs/IMAGE_RETARGETING_GUIDE.md` - Image retargeting details
- `PIPELINE_GUIDE.md` - Complete pipeline guide
- `docs/6DOF_CONTROL_GUIDE.md` - 6-DOF control system
- `docs/QUICKSTART.md` - Getting started guide

---

## 🆘 Troubleshooting

**No hand detected?**
- Ensure hand is clearly visible
- Try different lighting conditions
- Use `--visualize` to see MediaPipe detection

**Want to see intermediate results?**
```bash
# Add --save-annotated to see MediaPipe landmarks
python image_retargeting.py \
    --folder frames/ \
    --urdf brainco_hand/brainco_right.urdf \
    --hand right \
    --output annotated/ \
    --save-annotated
```
