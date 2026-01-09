# 图像手部重定向指南 (Image-based Hand Retargeting)

## 概述

除了视频输入，系统现在支持**从图像进行手部重定向**，包括：
- 📷 **单张图像** - 从单个照片提取手部姿态
- 🖼️ **图像序列** - 从连续图像帧生成运动轨迹
- 📋 **图像列表** - 处理自定义的图像集合

适用场景：
- 从静态照片生成机器人控制指令
- 处理相机拍摄的图像序列
- 分析关键帧的手部姿态
- 测试和调试手部检测

---

## 🚀 快速开始

### 安装
与视频重定向使用相同的依赖：
```bash
pip install -r requirements.txt
```

### 基本用法

#### 1. 单张图像
```bash
python image_retargeting.py \
    --image hand_photo.jpg \
    --urdf brainco_hand/brainco_right.urdf \
    --hand right
```

#### 2. 图像文件夹
```bash
python image_retargeting.py \
    --folder image_frames/ \
    --urdf brainco_hand/brainco_right.urdf \
    --hand right
```

#### 3. 使用自动化脚本
```bash
./run_image_retargeting.sh
```

---

## 📋 详细用法

### 模式 1: 单张图像处理

处理单个图像文件，提取手部关节角度。

```bash
python image_retargeting.py \
    --image path/to/hand.jpg \
    --urdf brainco_hand/brainco_right.urdf \
    --hand right
```

**输出：**
- 在屏幕上显示带标注的图像（按任意键关闭）
- 在终端打印11个关节角度（度数）
- 保存结果到 `single_image_result.json`

**示例输出：**
```
✓ Hand detected with 11 joint angles

✓ Joint Angles (degrees):
  right_thumb_metacarpal_joint: 45.23°
  right_thumb_proximal_joint: 30.15°
  right_thumb_distal_joint: 30.15°
  right_index_proximal_joint: 15.67°
  right_index_distal_joint: 18.10°
  ...
```

**不显示可视化窗口：**
```bash
python image_retargeting.py \
    --image hand.jpg \
    --urdf brainco_hand/brainco_right.urdf \
    --no-visualize
```

### 模式 2: 图像序列处理

处理文件夹中的多个图像，生成完整的运动轨迹。

```bash
python image_retargeting.py \
    --folder image_frames/ \
    --urdf brainco_hand/brainco_right.urdf \
    --hand right \
    --pattern "*.png" \
    --fps 30 \
    --output annotated_frames/
```

**参数说明：**
- `--folder`: 图像文件夹路径
- `--pattern`: 图像文件匹配模式（默认：`*.jpg`）
  - 支持：`*.jpg`, `*.png`, `*.jpeg`, `*.JPG`, `*.PNG`
- `--fps`: 假定的帧率（用于轨迹时间戳，默认：30）
- `--output`: 保存标注图像的文件夹（可选）

**输出文件：**
- `hand_trajectory.json` - 完整11-DOF轨迹
- `hand_trajectory_6dof.json` - 6-DOF可控轨迹
- `annotated_frames/` - 带标注的图像（如果指定了`--output`）

**示例输出：**
```
============================================
Processing Image Sequence
============================================
Folder: image_frames/
Total images: 150
Pattern: *.png
Assumed FPS: 30
============================================

Processed 10/150 | Detected: 9/10
Processed 20/150 | Detected: 18/20
...
Processed 150/150 | Detected: 145/150

Total images: 150
Hand detected: 145/150 (96.7%)

✓ Trajectory saved to: image_frames/hand_trajectory.json
✓ 6-DOF trajectory saved to: image_frames/hand_trajectory_6dof.json
```

### 模式 3: 自定义图像列表

处理指定的多个图像文件。

```bash
python image_retargeting.py \
    --list image1.jpg image2.jpg image3.jpg \
    --urdf brainco_hand/brainco_right.urdf \
    --hand right \
    --fps 10
```

**使用场景：**
- 处理不连续的关键帧
- 分析特定的手部姿态集合
- 从不同文件夹中选择图像

---

## 🎬 与视频重定向的对比

| 特性 | 视频重定向 | 图像重定向 |
|------|-----------|-----------|
| **输入** | .mp4, .avi 视频文件 | .jpg, .png 图像文件 |
| **处理速度** | 受视频解码影响 | 更快（无解码） |
| **适用场景** | 连续运动捕捉 | 静态姿态、关键帧 |
| **输出** | 完整运动轨迹 | 单帧或序列轨迹 |
| **FPS控制** | 由视频决定 | 用户指定 |
| **批量处理** | 单个视频 | 可处理文件夹 |

---

## 💡 使用技巧

### 1. 图像质量要求
- **分辨率**: 最低640x480，推荐1280x720或更高
- **光照**: 均匀光照，避免强烈阴影
- **手部清晰度**: 手部占据画面的合理比例（不要太小）
- **遮挡**: 避免手部被其他物体遮挡

### 2. 提高检测率
```bash
# 如果检测率低，尝试：
# 1. 调整图像大小
# 2. 提高图像亮度/对比度
# 3. 确保手部在画面中央
# 4. 避免复杂背景
```

### 3. 批量处理优化
```python
# Python脚本示例：预处理图像
import cv2
from pathlib import Path

input_folder = Path("raw_images/")
output_folder = Path("preprocessed/")
output_folder.mkdir(exist_ok=True)

for img_path in input_folder.glob("*.jpg"):
    img = cv2.imread(str(img_path))
    
    # 调整大小到固定分辨率
    img = cv2.resize(img, (1280, 720))
    
    # 提高对比度
    img = cv2.convertScaleAbs(img, alpha=1.2, beta=10)
    
    # 保存
    cv2.imwrite(str(output_folder / img_path.name), img)
```

### 4. 从视频提取关键帧
```bash
# 使用ffmpeg从视频提取图像
ffmpeg -i input_video.mp4 -vf fps=5 frames/frame_%04d.png

# 然后处理提取的帧
python image_retargeting.py \
    --folder frames/ \
    --pattern "*.png" \
    --fps 5 \
    --urdf brainco_hand/brainco_right.urdf
```

---

## 📊 输出格式

### 单张图像结果 (single_image_result.json)
```json
{
  "image_path": "hand_photo.jpg",
  "image_size": [1280, 720],
  "hand_detected": true,
  "angle_unit": "degrees",
  "joint_angles": {
    "right_thumb_metacarpal_joint": 45.23,
    "right_thumb_proximal_joint": 30.15,
    ...
  }
}
```

### 图像序列轨迹 (hand_trajectory.json)
```json
{
  "fps": 30.0,
  "angle_unit": "degrees",
  "source": "image_sequence",
  "source_folder": "image_frames/",
  "frames": [
    {
      "frame": 0,
      "timestamp": 0.0,
      "image_file": "frame_0001.png",
      "joint_angles": {
        "right_thumb_metacarpal_joint": 45.23,
        ...
      }
    },
    ...
  ]
}
```

### 6-DOF可控轨迹 (hand_trajectory_6dof.json)
与视频重定向生成的格式相同，包含：
- 6个可控关节角度
- Mimic关节信息
- 时间戳和FPS

可以直接用于机器人控制！

---

## 🔧 高级功能

### 1. 编程接口

```python
from image_retargeting import ImageHandRetargeting

# 初始化
retargeting = ImageHandRetargeting(
    urdf_path="brainco_hand/brainco_right.urdf",
    hand_side="right"
)

# 处理单张图像
result = retargeting.process_single_image(
    "hand.jpg",
    visualize=True
)

if result['hand_detected']:
    joint_angles = result['joint_angles']
    print(f"Detected {len(joint_angles)} joints")

# 处理图像序列
trajectory = retargeting.process_image_sequence(
    image_folder="frames/",
    output_folder="annotated/",
    fps=30.0,
    image_pattern="*.png"
)

# 处理图像列表
image_list = ["img1.jpg", "img2.jpg", "img3.jpg"]
trajectory = retargeting.process_image_list(
    image_paths=image_list,
    output_path="trajectory.json",
    fps=10.0
)
```

### 2. 与6-DOF控制集成

```bash
# 1. 从图像生成轨迹
python image_retargeting.py \
    --folder keyframes/ \
    --urdf brainco_hand/brainco_right.urdf \
    --fps 5

# 2. 查看6-DOF控制命令
python dof6_control.py \
    --trajectory keyframes/hand_trajectory_6dof.json \
    --frame 0

# 3. 导出为机器人控制格式
python dof6_control.py \
    --trajectory keyframes/hand_trajectory_6dof.json \
    --export csv
```

### 3. 可视化图像轨迹

```bash
# 使用PyBullet可视化
python visualize_revo2_hand.py \
    --urdf brainco_hand/brainco_right.urdf \
    --trajectory image_frames/hand_trajectory.json \
    --loop
```

---

## 🎯 应用场景

### 1. 机器人姿态示教
```bash
# 拍摄机械手目标姿态照片
# 然后提取关节角度作为目标姿态

python image_retargeting.py --image target_pose.jpg --urdf brainco_hand/brainco_right.urdf
# → 获得目标关节角度，发送给机器人
```

### 2. 手语识别数据集
```bash
# 处理手语图像数据集
python image_retargeting.py \
    --folder sign_language_dataset/ \
    --pattern "*.jpg" \
    --urdf brainco_hand/brainco_right.urdf
# → 生成手部关节角度数据集用于训练
```

### 3. 动作序列分析
```bash
# 从视频提取关键帧
ffmpeg -i action_video.mp4 -vf "select='eq(n\,0)+eq(n\,30)+eq(n\,60)'" -vsync 0 keyframes/frame_%d.png

# 分析关键帧
python image_retargeting.py \
    --folder keyframes/ \
    --urdf brainco_hand/brainco_right.urdf
# → 分析动作中的关键姿态
```

### 4. 手部姿态数据库
```python
# 构建手部姿态数据库
from image_retargeting import ImageHandRetargeting
import json

retargeting = ImageHandRetargeting("brainco_hand/brainco_right.urdf", "right")

pose_database = {}
for pose_name in ["open", "closed", "point", "pinch"]:
    result = retargeting.process_single_image(
        f"poses/{pose_name}.jpg",
        visualize=False
    )
    if result['hand_detected']:
        pose_database[pose_name] = result['joint_angles']

# 保存姿态库
with open('pose_database.json', 'w') as f:
    json.dump(pose_database, f, indent=2)
```

---

## 🆘 常见问题

### Q: 图像中检测不到手？
A: 
- 确保手部清晰可见，占据画面合理比例
- 检查光照是否充足
- 尝试调整图像大小或增强对比度
- 确保背景不要太复杂

### Q: 检测率很低（<80%）？
A:
- 检查图像质量和分辨率
- 确保手部没有被严重遮挡
- 尝试预处理图像（调整亮度、对比度）
- 检查手部是否在画面中央

### Q: 角度值看起来不对？
A:
- 确认使用了正确的`--hand`参数（left/right）
- 检查URDF文件路径是否正确
- 查看可视化结果确认关键点检测是否准确

### Q: 如何加快处理速度？
A:
- 关闭可视化：`--no-visualize`
- 不保存标注图像（不使用`--output`）
- 使用较小的图像分辨率
- 批量处理而不是逐个处理

### Q: 图像序列的FPS如何选择？
A:
- 如果图像是从视频提取的，使用视频的FPS
- 如果是相机拍摄的序列，使用相机的拍摄频率
- 默认值30 FPS适用于大多数场景
- FPS只影响时间戳，不影响角度计算

---

## 📝 总结

### 主要优势
✅ 支持单张图像和图像序列  
✅ 与视频重定向生成相同格式的输出  
✅ 可直接用于6-DOF机器人控制  
✅ 处理速度快，适合批量处理  
✅ 支持多种图像格式  

### 使用流程
```
图像输入
    ↓
MediaPipe手部检测
    ↓
关节角度计算 (11 DOF)
    ↓
输出轨迹 (JSON格式)
    ↓
提取6-DOF可控关节
    ↓
机器人控制或可视化
```

### 下一步
- 📖 查看 [`6DOF_CONTROL_GUIDE.md`](6DOF_CONTROL_GUIDE.md) 了解如何使用生成的轨迹
- 🎮 使用 `visualize_revo2_hand.py` 可视化轨迹
- 🤖 使用 `dof6_control.py` 导出机器人控制命令
- 📊 运行 `examples.py` 查看更多示例

---

**祝你使用愉快！** 📷✨

如有问题，请参考其他文档或提交issue。
