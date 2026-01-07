#!/bin/bash
# Quick start script for hand retargeting

echo "======================================"
echo "BrainCo Hand Retargeting System"
echo "======================================"
echo ""

# URDF Selection Menu
echo "Select URDF Model:"
echo "1. Revo2 Hand (Original, ROS2 version)"
echo "2. BrainCo Hand (New, with meshes)"
echo ""
read -p "Enter choice (1 or 2) [default: 1]: " URDF_CHOICE
URDF_CHOICE=${URDF_CHOICE:-1}

# Define paths based on selection
VIDEO_PATH="human_hand_video.mp4"
OUTPUT_VIDEO="output_annotated.mp4"
TRAJECTORY_FILE="hand_trajectory.json"
PLOT_FILE="trajectory_plot.png"

if [ "$URDF_CHOICE" = "2" ]; then
    URDF_PATH="brainco_hand/brainco_right.urdf"
    echo "Selected: BrainCo Hand URDF"
else
    URDF_PATH="Revo2_URDF Description_ROS2/revo2_description/urdf/revo2_right_hand.urdf"
    echo "Selected: Revo2 Hand URDF"
fi
echo ""

# Check if video exists
if [ ! -f "$VIDEO_PATH" ]; then
    echo "Error: Video file '$VIDEO_PATH' not found!"
    echo "Please ensure the video is in the current directory."
    exit 1
fi

# Check if URDF exists
if [ ! -f "$URDF_PATH" ]; then
    echo "Error: URDF file not found!"
    echo "Please check the path: $URDF_PATH"
    exit 1
fi

# Check if Python packages are installed
echo "Checking dependencies..."
python3 -c "import cv2, mediapipe, numpy, matplotlib" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Missing dependencies. Installing..."
    pip3 install -r requirements.txt
fi

echo ""
echo "Step 1: Processing video with hand retargeting..."
echo "--------------------------------------"
python3 hand_retargeting.py \
    --video "$VIDEO_PATH" \
    --urdf "$URDF_PATH" \
    --hand right \
    --output "$OUTPUT_VIDEO"

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Video processing complete!"
    echo "  - Output video: $OUTPUT_VIDEO"
    echo "  - Trajectory data: $TRAJECTORY_FILE"
else
    echo ""
    echo "✗ Video processing failed!"
    exit 1
fi

echo ""
echo "Step 2: Visualizing trajectory..."
echo "--------------------------------------"
python3 visualize_trajectory.py \
    --trajectory "$TRAJECTORY_FILE" \
    --output "$PLOT_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Visualization complete!"
    echo "  - Plot saved: $PLOT_FILE"
else
    echo ""
    echo "✗ Visualization failed!"
    exit 1
fi

echo ""
echo "======================================"
echo "All processing complete!"
echo "======================================"
echo ""
echo "Output files:"
echo "  1. $OUTPUT_VIDEO - Annotated video with hand tracking"
echo "  2. $TRAJECTORY_FILE - Joint angle trajectory data"
echo "  3. $PLOT_FILE - Trajectory visualization plot"
echo ""
