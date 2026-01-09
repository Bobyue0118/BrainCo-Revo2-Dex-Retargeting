# 6-DOF Robot Control Guide

## 概述

BrainCo机械手虽然有**11个关节**，但实际只有**6个可控自由度**。其余5个关节通过URDF的`<mimic>`机制自动跟随主关节运动。

这个设计简化了机器人控制，减少了电机数量和控制复杂度。

---

## 🤖 自由度分解

### 可控关节 (6 DOF) - 需要电机驱动

| 手指 | 关节 | URDF关节名 | 功能 |
|------|------|-----------|------|
| 拇指 | Metacarpal | `right_thumb_metacarpal_joint` | 拇指展收 |
| 拇指 | Proximal | `right_thumb_proximal_joint` | 拇指近端弯曲 |
| 食指 | Proximal | `right_index_proximal_joint` | 食指近端弯曲 |
| 中指 | Proximal | `right_middle_proximal_joint` | 中指近端弯曲 |
| 无名指 | Proximal | `right_ring_proximal_joint` | 无名指近端弯曲 |
| 小指 | Proximal | `right_pinky_proximal_joint` | 小指近端弯曲 |

### 从动关节 (5 DOF) - 通过传动跟随主关节

| 关节 | 跟随关节 | 传动比 | 公式 |
|------|---------|-------|------|
| `thumb_distal` | `thumb_proximal` | 1.0 | `θ_distal = 1.0 × θ_proximal` |
| `index_distal` | `index_proximal` | 1.155 | `θ_distal = 1.155 × θ_proximal` |
| `middle_distal` | `middle_proximal` | 1.155 | `θ_distal = 1.155 × θ_proximal` |
| `ring_distal` | `ring_proximal` | 1.155 | `θ_distal = 1.155 × θ_proximal` |
| `pinky_distal` | `pinky_proximal` | 1.155 | `θ_distal = 1.155 × θ_proximal` |

> **注意**: 四指的distal关节传动比为1.155，意味着远端关节弯曲幅度比近端关节大15.5%，这符合人手的自然弯曲模式。

---

## 📂 输出文件

处理视频后，系统会生成两个轨迹文件：

### 1. `hand_trajectory.json` - 完整11自由度轨迹
```json
{
  "fps": 30.0,
  "frames": [
    {
      "frame": 0,
      "timestamp": 0.0,
      "joint_angles": {
        "right_thumb_metacarpal_joint": 0.123,
        "right_thumb_proximal_joint": 0.456,
        "right_thumb_distal_joint": 0.456,      // 自动跟随
        "right_index_proximal_joint": 0.789,
        "right_index_distal_joint": 0.911,       // 自动跟随
        // ... 其他关节
      }
    }
  ]
}
```

### 2. `hand_trajectory_6dof.json` - 6自由度可控轨迹 ⭐
```json
{
  "fps": 30.0,
  "dof": 6,
  "joints": [
    "thumb_metacarpal",
    "thumb_proximal",
    "index_proximal",
    "middle_proximal",
    "ring_proximal",
    "pinky_proximal"
  ],
  "joint_names": [
    "right_thumb_metacarpal_joint",
    "right_thumb_proximal_joint",
    "right_index_proximal_joint",
    "right_middle_proximal_joint",
    "right_ring_proximal_joint",
    "right_pinky_proximal_joint"
  ],
  "mimic_info": {
    "right_thumb_distal_joint": {
      "parent": "right_thumb_proximal_joint",
      "multiplier": 1.0,
      "offset": 0.0
    },
    // ... 其他mimic关节
  },
  "frames": [
    {
      "right_thumb_metacarpal_joint": 0.123,
      "right_thumb_proximal_joint": 0.456,
      "right_index_proximal_joint": 0.789,
      "right_middle_proximal_joint": 0.234,
      "right_ring_proximal_joint": 0.567,
      "right_pinky_proximal_joint": 0.890
    }
  ]
}
```

---

## 🚀 使用方法

### 1. 生成6-DOF轨迹

运行重定向脚本时会自动生成：

```bash
python hand_retargeting.py \
    --video human_hand_video.mp4 \
    --urdf brainco_hand/brainco_right.urdf \
    --hand right \
    --output output_annotated.mp4
```

输出：
- ✅ `hand_trajectory.json` - 完整11-DOF轨迹
- ✅ `hand_trajectory_6dof.json` - 6-DOF可控轨迹

### 2. 查看轨迹信息

```bash
python dof6_control.py hand_trajectory_6dof.json
```

输出示例：
```
✓ Loaded 6-DOF trajectory from: hand_trajectory_6dof.json
  DOF: 6
  Frames: 621
  FPS: 30.0

📋 Controllable Joints:
  1. thumb_metacarpal      → right_thumb_metacarpal_joint
  2. thumb_proximal        → right_thumb_proximal_joint
  3. index_proximal        → right_index_proximal_joint
  4. middle_proximal       → right_middle_proximal_joint
  5. ring_proximal         → right_ring_proximal_joint
  6. pinky_proximal        → right_pinky_proximal_joint

🔗 Mimic Joints (automatically controlled):
  right_thumb_distal_joint
    └─ mimics: right_thumb_proximal_joint
       formula: angle = 1.0 * parent_angle + 0.0
  ...
```

### 3. 导出为控制格式

#### 导出为CSV（Excel/MATLAB使用）
```bash
python dof6_control.py hand_trajectory_6dof.json --export csv
```

生成 `control_trajectory_6dof.csv`:
```csv
frame,right_thumb_metacarpal_joint,right_thumb_proximal_joint,...
0,0.1234,0.5678,0.9012,...
1,0.1235,0.5679,0.9013,...
...
```

#### 导出为NumPy数组（Python使用）
```bash
python dof6_control.py hand_trajectory_6dof.json --export numpy
```

生成 `control_trajectory_6dof.npy` (可用`np.load()`加载)

#### 导出为文本（人类可读）
```bash
python dof6_control.py hand_trajectory_6dof.json --export text
```

### 4. 显示逐帧控制命令

```bash
python dof6_control.py hand_trajectory_6dof.json --show-frames
```

输出示例：
```
Frame 0 (t=0.000s):
  right_thumb_metacarpal_joint : 0.1234 rad (7.07°)
  right_thumb_proximal_joint   : 0.5678 rad (32.53°)
  right_index_proximal_joint   : 0.9012 rad (51.64°)
  ...
  
  → Mimic joint angles:
    right_thumb_distal_joint  : 0.5678 rad (32.53°)
    right_index_distal_joint  : 1.0409 rad (59.64°)
    ...

Frame 1 (t=0.033s):
  ...
```

### 5. 统计分析

```bash
python dof6_control.py hand_trajectory_6dof.json --stats
```

输出：
- 每个关节的角度范围
- 平均角度
- 运动范围
- 最大/最小值出现帧

---

## 💻 编程接口

### Python示例

```python
import json
import numpy as np

# 加载6-DOF轨迹
with open('hand_trajectory_6dof.json', 'r') as f:
    trajectory = json.load(f)

fps = trajectory['fps']
joint_names = trajectory['joint_names']
frames = trajectory['frames']

# 获取特定时间点的控制命令
def get_control_at_time(t: float):
    """获取时刻t的6个关节角度"""
    frame_idx = int(t * fps)
    if frame_idx >= len(frames):
        frame_idx = len(frames) - 1
    
    frame = frames[frame_idx]
    return [frame[joint] for joint in joint_names]

# 示例：获取1.5秒时的控制命令
angles = get_control_at_time(1.5)
print(f"Control command at t=1.5s:")
for joint, angle in zip(joint_names, angles):
    print(f"  {joint}: {angle:.4f} rad ({np.degrees(angle):.2f}°)")

# 计算mimic关节角度
mimic_info = trajectory['mimic_info']

def compute_mimic_angles(controllable_angles: dict) -> dict:
    """从可控关节计算所有mimic关节角度"""
    all_angles = controllable_angles.copy()
    
    for mimic_joint, info in mimic_info.items():
        parent_joint = info['parent']
        multiplier = info['multiplier']
        offset = info['offset']
        
        parent_angle = controllable_angles[parent_joint]
        all_angles[mimic_joint] = multiplier * parent_angle + offset
    
    return all_angles

# 示例：计算某一帧的所有11个关节角度
frame_0 = frames[0]
all_angles = compute_mimic_angles(frame_0)
print(f"\nAll 11 joint angles for frame 0:")
for joint, angle in all_angles.items():
    print(f"  {joint}: {angle:.4f} rad")
```

### C++/ROS示例

```cpp
#include <fstream>
#include <nlohmann/json.hpp>  // JSON library

// 加载6-DOF轨迹
std::ifstream file("hand_trajectory_6dof.json");
nlohmann::json trajectory = nlohmann::json::parse(file);

double fps = trajectory["fps"];
auto frames = trajectory["frames"];
auto joint_names = trajectory["joint_names"];

// 获取某一帧的控制命令
int frame_idx = 100;
std::vector<double> control_cmd;
for (const auto& joint : joint_names) {
    control_cmd.push_back(frames[frame_idx][joint]);
}

// 发送到机器人控制器
send_joint_command(control_cmd);

// 计算mimic关节
auto mimic_info = trajectory["mimic_info"];
std::map<std::string, double> all_angles;

// 复制可控关节
for (size_t i = 0; i < joint_names.size(); ++i) {
    all_angles[joint_names[i]] = control_cmd[i];
}

// 计算mimic关节
for (auto& [mimic_joint, info] : mimic_info.items()) {
    std::string parent = info["parent"];
    double multiplier = info["multiplier"];
    double offset = info["offset"];
    
    all_angles[mimic_joint] = multiplier * all_angles[parent] + offset;
}
```

---

## 🔧 机器人集成建议

### 1. 控制频率匹配

如果轨迹FPS=30，但机器人控制频率=100Hz：

```python
# 使用插值生成更高频率的控制命令
from scipy.interpolate import interp1d

# 原始时间轴
t_original = np.arange(len(frames)) / fps

# 新的时间轴（100Hz）
robot_control_freq = 100
t_new = np.arange(0, len(frames)/fps, 1/robot_control_freq)

# 对每个关节进行插值
for joint_name in joint_names:
    angles = [frame[joint_name] for frame in frames]
    interpolator = interp1d(t_original, angles, kind='cubic')
    new_angles = interpolator(t_new)
    # 发送new_angles到机器人
```

### 2. 速度和加速度限制

```python
def apply_velocity_limits(trajectory, max_velocity):
    """限制关节速度"""
    limited_trajectory = [trajectory[0]]
    
    for i in range(1, len(trajectory)):
        dt = 1.0 / fps
        prev_angles = limited_trajectory[-1]
        curr_angles = trajectory[i]
        
        limited_angles = {}
        for joint in joint_names:
            delta = curr_angles[joint] - prev_angles[joint]
            velocity = delta / dt
            
            # 限制速度
            if abs(velocity) > max_velocity:
                delta = max_velocity * dt * np.sign(velocity)
            
            limited_angles[joint] = prev_angles[joint] + delta
        
        limited_trajectory.append(limited_angles)
    
    return limited_trajectory
```

### 3. 碰撞检测和关节限制

```python
# 从URDF读取关节限制
joint_limits = {
    'right_thumb_metacarpal_joint': (-0.2618, 0.5236),  # -15° ~ 30°
    'right_thumb_proximal_joint': (0.0, 1.5708),        # 0° ~ 90°
    # ... 其他关节
}

def apply_joint_limits(angles):
    """应用关节限制"""
    safe_angles = {}
    for joint, angle in angles.items():
        if joint in joint_limits:
            lower, upper = joint_limits[joint]
            safe_angles[joint] = np.clip(angle, lower, upper)
        else:
            safe_angles[joint] = angle
    return safe_angles
```

---

## 📊 示例：运行example 6

```bash
# 运行6-DOF控制示例
python examples.py 6
```

输出：
```
============================================================
EXAMPLE 6: 6-DOF Robot Control (BrainCo Hand)
============================================================

✓ Loaded 6-DOF trajectory
  Frames: 621
  FPS: 30.0
  Duration: 20.70 seconds

📋 Controllable Joints (6 DOF):
  1. thumb_metacarpal      → right_thumb_metacarpal_joint
  2. thumb_proximal        → right_thumb_proximal_joint
  3. index_proximal        → right_index_proximal_joint
  4. middle_proximal       → right_middle_proximal_joint
  5. ring_proximal         → right_ring_proximal_joint
  6. pinky_proximal        → right_pinky_proximal_joint

🔗 Mimic Joints (auto-computed from controllable joints):
  • right_thumb_distal_joint
    └─ mimics: right_thumb_proximal_joint
       formula: angle = 1.0 × parent_angle + 0.0
  ...

📊 Sample Frame (frame 100):
  Controllable joint angles (radians):
    right_thumb_metacarpal_joint:  0.1234 rad ( 7.07°)
    right_thumb_proximal_joint:    0.5678 rad (32.53°)
    ...

💾 Exporting to CSV: control_trajectory_6dof.csv
✓ CSV export complete: control_trajectory_6dof.csv

💡 You can now use this CSV file with your robot control system!
   Each row = control command for one time step
   Columns = 6 controllable joint angles in radians
```

---

## 📝 总结

### 关键要点

1. **只需控制6个关节** - 其余5个通过机械传动自动跟随
2. **两种输出格式** - 11-DOF完整轨迹 + 6-DOF可控轨迹
3. **多种导出格式** - CSV, NumPy, Text
4. **包含Mimic信息** - 可以从6-DOF重建11-DOF
5. **易于集成** - 简单的JSON格式，支持各种编程语言

### 控制流程

```
人手视频
    ↓
MediaPipe检测 (21个关键点)
    ↓
重定向算法 (映射到11个机械手关节)
    ↓
保存为 hand_trajectory.json (11 DOF)
    ↓
提取可控关节 → hand_trajectory_6dof.json (6 DOF)
    ↓
导出为控制格式 (CSV/NumPy/Text)
    ↓
发送到机器人控制器 → 6个电机
    ↓
机械传动 → 5个从动关节自动跟随
    ↓
完整的11自由度手部运动！
```

### 优势

- ✅ **简化控制** - 只需6个控制信号，不是11个
- ✅ **降低成本** - 少5个电机和驱动器
- ✅ **保持自然** - Mimic传动比模拟人手的自然运动
- ✅ **易于调试** - 少量控制变量，问题更容易定位
- ✅ **通用格式** - JSON/CSV可被任何系统读取

---

## 🆘 故障排除

### Q: 生成的轨迹没有6-DOF文件？
A: 确保使用最新版本的`hand_retargeting.py`，并且使用了BrainCo URDF（不是Revo2）

### Q: Mimic关节角度看起来不对？
A: 检查URDF中的`<mimic>`标签，确认multiplier和offset值

### Q: 如何验证6-DOF轨迹？
A: 使用`visualize_revo2_hand.py`加载`hand_trajectory_6dof.json`进行可视化验证

### Q: CSV文件中的角度单位是什么？
A: 始终是**弧度**（radians）。转换为度：`degrees = radians * 180 / π`

---

**祝你控制顺利！** 🤖✨

如有问题，请查看其他文档或提交issue。
