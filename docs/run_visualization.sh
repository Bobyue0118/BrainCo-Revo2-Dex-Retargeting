#!/bin/bash
# Quick start script for 3D visualization

echo "======================================"
echo "BrainCo Hand 3D Visualization"
echo "======================================"
echo ""

# URDF Selection Menu
echo "Select URDF Model:"
echo "1. Revo2 Hand (Original, ROS2 version)"
echo "2. BrainCo Hand (New, with meshes)"
echo ""
read -p "Enter choice (1 or 2) [default: 1]: " URDF_CHOICE
URDF_CHOICE=${URDF_CHOICE:-1}

if [ "$URDF_CHOICE" = "2" ]; then
    URDF_PATH="brainco_hand/brainco_right.urdf"
    echo "Selected: BrainCo Hand URDF"
else
    URDF_PATH="Revo2_URDF Description_ROS2/revo2_description/urdf/revo2_right_hand.urdf"
    echo "Selected: Revo2 Hand URDF"
fi
echo ""

TRAJECTORY_FILE="hand_trajectory.json"

# Check if URDF exists
if [ ! -f "$URDF_PATH" ]; then
    echo "Error: URDF file not found!"
    echo "Please check the path: $URDF_PATH"
    exit 1
fi

# Check if trajectory file exists
if [ ! -f "$TRAJECTORY_FILE" ]; then
    echo "Warning: Trajectory file not found: $TRAJECTORY_FILE"
    echo "You need to run hand retargeting first to generate the trajectory."
    echo ""
    read -p "Do you want to run retargeting now? (y/n): " response
    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        ./run_retargeting.sh
    else
        echo "Exiting. Please run './run_retargeting.sh' first."
        exit 1
    fi
fi

echo ""
echo "Choose visualization mode:"
echo "  1. PyBullet - Replay trajectory (fast, interactive)"
echo "  2. SAPIEN - Advanced physics & rendering (NEW! 🎨)"
echo "  3. Real-time - Video + 3D side-by-side"
echo ""
read -p "Enter choice (1, 2, or 3): " choice

if [ "$choice" = "1" ]; then
    echo ""
    echo "Starting PyBullet 3D trajectory replay..."
    echo "--------------------------------------"
    python3 visualize_revo2_hand.py \
        --urdf "$URDF_PATH" \
        --trajectory "$TRAJECTORY_FILE" \
        --speed 1.0 \
        --loop

elif [ "$choice" = "2" ]; then
    echo ""
    echo "Starting SAPIEN visualization..."
    echo "--------------------------------------"
    
    # Check if SAPIEN is installed
    python3 -c "import sapien.core" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "⚠️  SAPIEN is not available on this system."
        echo ""
        echo "SAPIEN may not support your platform (especially macOS ARM)."
        echo ""
        echo "Would you like to:"
        echo "  1. Try installing SAPIEN anyway"
        echo "  2. Use PyBullet instead (recommended)"
        echo "  3. Cancel"
        echo ""
        read -p "Enter choice (1, 2, or 3): " install_choice
        
        if [ "$install_choice" = "1" ]; then
            echo "Attempting to install SAPIEN..."
            pip3 install sapien
            if [ $? -ne 0 ]; then
                echo ""
                echo "✗ SAPIEN installation failed."
                echo "This is likely due to platform incompatibility."
                echo ""
                read -p "Fall back to PyBullet? (y/n): " fallback
                if [ "$fallback" = "y" ] || [ "$fallback" = "Y" ]; then
                    choice="1"
                else
                    exit 1
                fi
            fi
        elif [ "$install_choice" = "2" ]; then
            echo ""
            echo "Switching to PyBullet..."
            choice="1"
        else
            echo "Cancelled."
            exit 0
        fi
    fi
    
    if [ "$choice" = "2" ]; then
        python3 visualize_sapien.py \
            --urdf "$URDF_PATH" \
            --trajectory "$TRAJECTORY_FILE" \
            --speed 1.0 \
            --loop
    fi
    
elif [ "$choice" = "1" ]; then
    echo ""
    echo "Starting PyBullet 3D trajectory replay..."
    echo "--------------------------------------"
    python3 visualize_revo2_hand.py \
        --urdf "$URDF_PATH" \
        --trajectory "$TRAJECTORY_FILE" \
        --speed 1.0 \
        --loop
    
elif [ "$choice" = "3" ]; then
    echo ""
    echo "Starting real-time visualization..."
    echo "--------------------------------------"
    
    if [ ! -f "human_hand_video.mp4" ]; then
        echo "Error: Video file 'human_hand_video.mp4' not found!"
        exit 1
    fi
    
    python3 realtime_visualize.py \
        --video human_hand_video.mp4 \
        --urdf "$URDF_PATH" \
        --hand right
else
    echo "Invalid choice!"
    exit 1
fi

echo ""
echo "======================================"
echo "Visualization complete!"
echo "======================================"
