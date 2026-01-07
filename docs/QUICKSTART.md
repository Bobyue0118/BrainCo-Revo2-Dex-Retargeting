# 快速入门指南 (Quick Start Guide)

## 🤖 选择手部模型

系统支持两种URDF模型：

1. **Revo2 Hand** (原版): `Revo2_URDF Description_ROS2/revo2_description/urdf/revo2_right_hand.urdf`
2. **BrainCo Hand** (新版): `brainco_hand/brainco_right.urdf`

两者具有相同的11自由度关节结构，完全兼容所有脚本。

---

## 1. 安装依赖

```bash
pip install -r requirements.txt
```

## 2. 运行重定向

### 方法 A: 使用自动化脚本（推荐）

```bash
./run_retargeting.sh
```

**脚本会提示您选择URDF模型：**
- 输入 `1` 使用 Revo2 Hand (原版)
- 输入 `2` 使用 BrainCo Hand (新版)

### 方法 B: 手动运行

**使用 Revo2 Hand:**
```bash
python hand_retargeting.py \
    --video human_hand_video.mp4 \
    --urdf "Revo2_URDF Description_ROS2/revo2_description/urdf/revo2_right_hand.urdf" \
    --hand right \
    --output output_annotated.mp4
```

**使用 BrainCo Hand:**
```bash
python hand_retargeting.py \
    --video human_hand_video.mp4 \
    --urdf "brainco_hand/brainco_right.urdf" \
    --hand right \
    --output output_annotated.mp4
```

**可视化结果:**
```bash
python visualize_trajectory.py --trajectory hand_trajectory.json
```

## 3. 3D 可视化 (NEW! 🎉)

### 方法 A: 使用可视化脚本（推荐）

```bash
./run_visualization.sh
```

**脚本会提示您：**
1. 选择URDF模型 (Revo2 或 BrainCo)
2. 选择可视化模式：
   - **选项 1**: 3D 轨迹回放（从保存的文件）
   - **选项 2**: 实时视频 + 3D（并排显示）

### 方法 B: 手动运行

**使用 Revo2 Hand:**
```bash
# 回放保存的轨迹
python visualize_revo2_hand.py \
    --urdf "Revo2_URDF Description_ROS2/revo2_description/urdf/revo2_right_hand.urdf" \
    --trajectory hand_trajectory.json \
    --loop

# 实时可视化
python realtime_visualize.py \
    --video human_hand_video.mp4 \
    --urdf "Revo2_URDF Description_ROS2/revo2_description/urdf/revo2_right_hand.urdf" \
    --hand right
```

**使用 BrainCo Hand:**
```bash
# 回放保存的轨迹
python visualize_revo2_hand.py \
    --urdf "brainco_hand/brainco_right.urdf" \
    --trajectory hand_trajectory.json \
    --loop

# 实时可视化
python realtime_visualize.py \
    --video human_hand_video.mp4 \
    --urdf "brainco_hand/brainco_right.urdf" \
    --hand right
```

## 4. 输出文件

- `output_annotated.mp4` - 带标注的视频
- `hand_trajectory.json` - 关节角度轨迹数据
- `trajectory_plot.png` - 轨迹可视化图表

## 4. 查看示例

```bash
# 查看所有可用示例
python examples.py

# 运行特定示例
python examples.py 1  # 基础用法
python examples.py 2  # 轨迹分析
python examples.py 3  # 导出 CSV
python examples.py 4  # 自定义映射
python examples.py 5  # 运动统计
```

## 支持的手部关节

### Revo2 右手 (11 自由度)

**拇指 (3 DOF)**
- thumb_metacarpal_joint (CMC关节)
- thumb_proximal_joint (MCP关节)
- thumb_distal_joint (IP关节)

**食指 (2 DOF)**
- index_proximal_joint
- index_distal_joint

**中指 (2 DOF)**
- middle_proximal_joint
- middle_distal_joint

**无名指 (2 DOF)**
- ring_proximal_joint
- ring_distal_joint

**小指 (2 DOF)**
- pinky_proximal_joint
- pinky_distal_joint

## 常见问题

### Q: 检测不到手？
A: 确保视频中手部清晰可见，光照充足

### Q: 处理速度慢？
A: MediaPipe 在 CPU 上运行可能较慢，考虑使用较短的视频进行测试

### Q: 关节角度不准确？
A: 检查 `--hand` 参数是否设置正确（left/right）

## 技术支持

详细文档请参考 `README_RETARGETING.md`
