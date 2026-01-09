# 完整Pipeline：图像到6-DOF机器人控制

## 概述

这个完整pipeline脚本将**图像文件夹**自动处理成**6-DOF机器人控制命令**和**重定向后的机械手可视化图像**。

```
图像文件夹
    ↓
[1] 手部检测 + 重定向
    ↓
[2] 渲染机械手姿态
    ↓
[3] 导出控制命令
    ↓
输出完整的控制数据包
```

---

## 🚀 快速开始

### 基本用法

```bash
python image_to_6dof_pipeline.py \
    --input image_frames/ \
    --urdf brainco_hand/brainco_right.urdf \
    --hand right \
    --output result/ \
    --fps 30
```

### 使用Shell脚本

```bash
./run_image_retargeting.sh
# 选择 "2) Image folder (sequence)"
```

---

## 📂 输出结构

Pipeline会生成一个完整的输出文件夹，包含所有需要的数据：

```
output_folder/
├── annotated_images/              # 原始图像 + 手部关键点标注
│   ├── annotated_frame_001.jpg
│   ├── annotated_frame_002.jpg
│   └── ...
│
├── rendered_hand_poses/           # 重定向后的机械手可视化 ⭐
│   ├── hand_pose_0000.jpg
│   ├── hand_pose_0001.jpg
│   └── ...
│
├── trajectories/                  # 关节角度轨迹文件
│   ├── hand_trajectory.json       (完整11-DOF轨迹)
│   └── hand_trajectory_6dof.json  (6-DOF可控轨迹) ⭐
│
└── control_commands/              # 机器人控制命令 ⭐
    └── control_trajectory_6dof.csv
```

### 文件说明

#### 1. `annotated_images/` - 检测可视化
- 原始图像 + MediaPipe检测的21个手部关键点
- 用于验证手部检测是否准确
- JPEG格式，可直接查看

#### 2. `rendered_hand_poses/` ⭐ - 机械手重定向可视化
- **最重要的输出**：展示重定向后的机械手姿态
- 使用PyBullet渲染的3D机械手图像
- 每一帧对应一个输入图像
- 可以验证重定向效果

#### 3. `trajectories/` - 轨迹数据

**hand_trajectory.json (11-DOF 完整轨迹)**
```json
{
  "fps": 30.0,
  "angle_unit": "degrees",
  "source": "image_sequence",
  "frames": [
    {
      "frame": 0,
      "timestamp": 0.0,
      "image_file": "frame_001.jpg",
      "joint_angles": {
        "right_thumb_metacarpal_joint": 75.23,
        "right_thumb_proximal_joint": 30.15,
        "right_thumb_distal_joint": 30.15,
        ...
      }
    }
  ]
}
```

**hand_trajectory_6dof.json (6-DOF 可控轨迹)** ⭐
```json
{
  "fps": 30.0,
  "dof": 6,
  "angle_unit": "degrees",
  "joints": [
    "thumb_metacarpal",
    "thumb_proximal",
    "index_proximal",
    "middle_proximal",
    "ring_proximal",
    "pinky_proximal"
  ],
  "mimic_info": {
    "right_thumb_distal_joint": {
      "parent": "right_thumb_proximal_joint",
      "multiplier": 1.0,
      "offset": 0.0
    },
    ...
  },
  "frames": [
    {
      "right_thumb_metacarpal_joint": 75.23,
      "right_thumb_proximal_joint": 30.15,
      "right_index_proximal_joint": 15.67,
      "right_middle_proximal_joint": 20.45,
      "right_ring_proximal_joint": 18.90,
      "right_pinky_proximal_joint": 22.13
    }
  ]
}
```

#### 4. `control_commands/control_trajectory_6dof.csv` ⭐ - 机器人控制命令

CSV格式，可直接用于机器人控制系统：

```csv
frame,right_thumb_metacarpal_joint,right_thumb_proximal_joint,right_index_proximal_joint,right_middle_proximal_joint,right_ring_proximal_joint,right_pinky_proximal_joint
0,75.23,30.15,15.67,20.45,18.90,22.13
1,75.45,30.20,15.70,20.50,18.95,22.15
2,75.67,30.25,15.73,20.55,19.00,22.18
...
```

**列说明：**
- `frame`: 帧编号
- 后续6列: 6个可控关节的角度（度数）

**发送到机器人的步骤：**
1. 读取CSV文件
2. 逐行发送6个关节角度
3. 其余5个关节（distal joints）通过机械传动自动跟随

---

## 🎯 使用场景

### 1. 从照片生成机器人控制序列

```bash
# 1. 拍摄一系列手部动作照片
# photos/
#   ├── pose_001.jpg
#   ├── pose_002.jpg
#   └── ...

# 2. 运行pipeline
python image_to_6dof_pipeline.py \
    --input photos/ \
    --urdf brainco_hand/brainco_right.urdf \
    --hand right \
    --output robot_demo/ \
    --fps 2  # 假设每秒2帧

# 3. 发送控制命令到机器人
# 读取 robot_demo/control_commands/control_trajectory_6dof.csv
```

### 2. 验证重定向效果

```bash
# 1. 运行pipeline
python image_to_6dof_pipeline.py --input frames/ --urdf brainco_hand/brainco_right.urdf --output result/

# 2. 对比原始图像和渲染结果
# result/annotated_images/    (人手 + 关键点)
# result/rendered_hand_poses/  (机械手姿态)

# 3. 并排显示对比
python compare_results.py result/
```

### 3. 批量处理数据集

```bash
# 处理多个手势的图像序列
for gesture in open close point pinch; do
    python image_to_6dof_pipeline.py \
        --input dataset/${gesture}/ \
        --urdf brainco_hand/brainco_right.urdf \
        --output results/${gesture}/ \
        --fps 30
done

# 每个手势都会生成完整的输出
```

### 4. 从视频提取并处理

```bash
# 1. 从视频提取帧
mkdir video_frames
ffmpeg -i demo_video.mp4 -vf fps=10 video_frames/frame_%04d.jpg

# 2. 运行pipeline
python image_to_6dof_pipeline.py \
    --input video_frames/ \
    --urdf brainco_hand/brainco_right.urdf \
    --output video_result/ \
    --fps 10

# 3. 可选：将渲染结果合成为视频
ffmpeg -framerate 10 -i video_result/rendered_hand_poses/hand_pose_%04d.jpg \
    -c:v libx264 -pix_fmt yuv420p retargeted_hand.mp4
```

---

## 🔧 高级选项

### 命令行参数

```bash
python image_to_6dof_pipeline.py [OPTIONS]
```

**必需参数：**
- `--input PATH`: 输入图像文件夹路径
- `--urdf PATH`: URDF文件路径
- `--hand {left,right}`: 手部类型（左手/右手）
- `--output PATH`: 输出文件夹路径

**可选参数：**
- `--fps FLOAT`: 假定帧率（默认：30.0）
  - 用于计算时间戳
  - 不影响角度计算
- `--pattern STRING`: 图像文件匹配模式（默认：`*.jpg`）
  - 例如：`*.png`, `*.jpeg`, `frame_*.jpg`
- `--width INT`: 渲染图像宽度（默认：640）
- `--height INT`: 渲染图像高度（默认：480）
- `--no-render`: 跳过机械手渲染步骤
- `--no-export`: 跳过CSV导出步骤

### 示例

#### 高分辨率渲染
```bash
python image_to_6dof_pipeline.py \
    --input frames/ \
    --urdf brainco_hand/brainco_right.urdf \
    --hand right \
    --output high_res_result/ \
    --width 1920 \
    --height 1080
```

#### 仅生成轨迹（不渲染）
```bash
python image_to_6dof_pipeline.py \
    --input frames/ \
    --urdf brainco_hand/brainco_right.urdf \
    --hand right \
    --output quick_result/ \
    --no-render
```

#### 自定义图像模式和FPS
```bash
python image_to_6dof_pipeline.py \
    --input png_frames/ \
    --pattern "*.png" \
    --fps 60 \
    --urdf brainco_hand/brainco_right.urdf \
    --hand right \
    --output result/
```

---

## 💻 编程接口

可以在Python脚本中调用pipeline：

```python
from image_to_6dof_pipeline import ImageTo6DOFPipeline

# 创建pipeline实例
pipeline = ImageTo6DOFPipeline(
    urdf_path="brainco_hand/brainco_right.urdf",
    hand_side="right"
)

# 运行pipeline
results = pipeline.run(
    input_folder="image_frames/",
    output_folder="result/",
    fps=30.0,
    image_pattern="*.jpg",
    render_width=640,
    render_height=480,
    skip_render=False,
    skip_export=False
)

# 访问结果
print(f"Detected: {results['detected_frames']}/{results['total_frames']}")
print(f"6-DOF trajectory: {results['trajectory_6dof_path']}")
print(f"Control CSV: {results['control_csv_path']}")
print(f"Rendered images: {results['rendered_folder']}")

# 读取6-DOF轨迹
import json
with open(results['trajectory_6dof_path'], 'r') as f:
    trajectory = json.load(f)

# 读取控制命令CSV
import pandas as pd
control_df = pd.read_csv(results['control_csv_path'])
print(control_df.head())
```

### 批量处理示例

```python
from image_to_6dof_pipeline import ImageTo6DOFPipeline
from pathlib import Path

pipeline = ImageTo6DOFPipeline(
    urdf_path="brainco_hand/brainco_right.urdf",
    hand_side="right"
)

# 处理多个文件夹
input_folders = [
    "dataset/gesture_open/",
    "dataset/gesture_close/",
    "dataset/gesture_point/"
]

for folder in input_folders:
    folder_name = Path(folder).name
    output_folder = f"results/{folder_name}/"
    
    print(f"\nProcessing {folder}...")
    results = pipeline.run(
        input_folder=folder,
        output_folder=output_folder,
        fps=30.0
    )
    
    print(f"✓ {folder_name}: {results['detected_frames']}/{results['total_frames']} frames")
```

---

## 📊 与机器人集成

### 1. Python机器人控制

```python
import pandas as pd
import time

# 读取控制命令
df = pd.read_csv('result/control_commands/control_trajectory_6dof.csv')

# 假设有机器人控制API
import robot_controller

robot = robot_controller.connect()
fps = 30.0  # 或从trajectory JSON读取
dt = 1.0 / fps

# 逐帧发送控制命令
for idx, row in df.iterrows():
    # 提取6个关节角度（度数）
    angles_deg = [
        row['right_thumb_metacarpal_joint'],
        row['right_thumb_proximal_joint'],
        row['right_index_proximal_joint'],
        row['right_middle_proximal_joint'],
        row['right_ring_proximal_joint'],
        row['right_pinky_proximal_joint']
    ]
    
    # 转换为弧度（如果机器人需要弧度）
    angles_rad = [deg * 3.14159 / 180 for deg in angles_deg]
    
    # 发送到机器人
    robot.set_joint_positions(angles_rad)
    
    # 等待下一帧
    time.sleep(dt)
    
    print(f"Frame {idx}/{len(df)} sent")

robot.disconnect()
```

### 2. ROS Integration

```python
#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import JointState
import pandas as pd

# 初始化ROS节点
rospy.init_node('hand_trajectory_player')
pub = rospy.Publisher('/joint_commands', JointState, queue_size=10)

# 读取轨迹
df = pd.read_csv('result/control_commands/control_trajectory_6dof.csv')

# 关节名称（6个可控关节）
joint_names = [
    'right_thumb_metacarpal_joint',
    'right_thumb_proximal_joint',
    'right_index_proximal_joint',
    'right_middle_proximal_joint',
    'right_ring_proximal_joint',
    'right_pinky_proximal_joint'
]

rate = rospy.Rate(30)  # 30 Hz

for idx, row in df.iterrows():
    if rospy.is_shutdown():
        break
    
    # 创建JointState消息
    msg = JointState()
    msg.header.stamp = rospy.Time.now()
    msg.name = joint_names
    msg.position = [row[name] * 3.14159 / 180 for name in joint_names]  # 转弧度
    
    pub.publish(msg)
    rate.sleep()
```

### 3. CSV直接导入

大多数机器人控制软件支持CSV导入：
- **ABB RobotStudio**: 导入CSV作为路径点
- **KUKA WorkVisual**: 导入关节角度序列
- **Universal Robots**: UR Script中读取CSV
- **Fanuc ROBOGUIDE**: 导入为运动程序

---

## 🎨 可视化对比

### 创建并排对比图

```python
import cv2
import numpy as np
from pathlib import Path

def create_comparison(annotated_path, rendered_path, output_path):
    """并排显示原始图像和渲染结果"""
    img1 = cv2.imread(annotated_path)
    img2 = cv2.imread(rendered_path)
    
    # 调整大小使其一致
    h, w = img1.shape[:2]
    img2 = cv2.resize(img2, (w, h))
    
    # 并排拼接
    combined = np.hstack([img1, img2])
    
    # 添加标签
    cv2.putText(combined, "Original + Detection", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(combined, "Retargeted Hand", (w + 10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imwrite(output_path, combined)

# 批量生成对比图
result_folder = Path("result/")
comparison_folder = result_folder / "comparisons"
comparison_folder.mkdir(exist_ok=True)

annotated_images = sorted((result_folder / "annotated_images").glob("*.jpg"))
rendered_images = sorted((result_folder / "rendered_hand_poses").glob("*.jpg"))

for ann_path, ren_path in zip(annotated_images, rendered_images):
    output_path = str(comparison_folder / f"comparison_{ann_path.stem}.jpg")
    create_comparison(str(ann_path), str(ren_path), output_path)
    print(f"✓ Created {output_path}")
```

### 生成对比视频

```bash
# 1. 创建并排视频（左：原始，右：渲染）
ffmpeg -i result/annotated_images/annotated_frame_%04d.jpg -i result/rendered_hand_poses/hand_pose_%04d.jpg \
    -filter_complex "[0:v][1:v]hstack=inputs=2" \
    -c:v libx264 -pix_fmt yuv420p comparison.mp4

# 2. 添加标题
ffmpeg -i comparison.mp4 -vf "drawtext=text='Original':x=10:y=10:fontsize=24:fontcolor=white, \
    drawtext=text='Retargeted':x=w/2+10:y=10:fontsize=24:fontcolor=white" \
    comparison_labeled.mp4
```

---

## 🆘 常见问题

### Q: 渲染的机械手图像是黑的？
A: PyBullet渲染问题。尝试：
- 更新PyBullet: `pip install pybullet --upgrade`
- 使用`--no-render`跳过渲染，单独运行：
  ```bash
  python render_hand_poses.py \
      --trajectory result/trajectories/hand_trajectory.json \
      --urdf brainco_hand/brainco_right.urdf \
      --output result/rendered_hand_poses/
  ```

### Q: 检测率很低（<80%）？
A: 
- 检查图像质量和光照
- 确保手部清晰可见
- 预处理图像（增强对比度）
- 查看`annotated_images/`确认检测质量

### Q: CSV文件中的角度单位是什么？
A: **度数（degrees）**。如果机器人需要弧度：
```python
angle_rad = angle_deg * 3.14159 / 180
```

### Q: 如何加快处理速度？
A:
- 使用`--no-render`跳过渲染（最耗时）
- 降低渲染分辨率（`--width 320 --height 240`）
- 使用更少的图像

### Q: 渲染的手部姿态不对？
A:
- 检查使用了正确的URDF（BrainCo vs Revo2）
- 确认`--hand`参数正确（left/right）
- 查看`annotated_images/`确认关键点检测准确

---

## 📝 总结

### Pipeline优势
✅ **一键处理** - 从图像到控制命令全自动  
✅ **完整输出** - 包含检测、轨迹、渲染、控制命令  
✅ **易于集成** - CSV格式直接用于机器人控制  
✅ **可视化验证** - 渲染的机械手图像验证重定向效果  
✅ **灵活配置** - 支持多种参数和输出选项  

### 输出文件用途
| 文件 | 用途 |
|------|------|
| `annotated_images/` | 验证手部检测质量 |
| `rendered_hand_poses/` ⭐ | 验证重定向效果 |
| `hand_trajectory_6dof.json` ⭐ | Python/ROS集成 |
| `control_trajectory_6dof.csv` ⭐ | 机器人直接控制 |

### 完整工作流

```
📷 拍摄手部动作图像序列
    ↓
🤖 运行 image_to_6dof_pipeline.py
    ↓
📊 检查检测率和渲染质量
    ↓
📁 获取完整输出包
    ↓
🔧 发送CSV到机器人控制系统
    ↓
✅ 机器人执行重定向动作！
```

---

**Happy Retargeting!** 🎉🤖

更多信息请参考其他文档：
- [6-DOF控制指南](docs/6DOF_CONTROL_GUIDE.md)
- [图像重定向指南](docs/IMAGE_RETARGETING_GUIDE.md)
- [快速开始](docs/QUICKSTART.md)
