#!/bin/bash

# Image-based Hand Retargeting Script
# Supports single image, image folders, or image lists

echo "=============================================="
echo "  Image-based Hand Retargeting"
echo "=============================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found. Please install Python 3.8+"
    exit 1
fi

# Function to select URDF
select_urdf() {
    echo "Select URDF model:"
    echo "  1) Revo2 Hand (original)"
    echo "  2) BrainCo Hand (new)"
    read -p "Enter choice [1-2]: " urdf_choice
    
    case $urdf_choice in
        1)
            URDF_PATH="Revo2_URDF Description_ROS2/revo2_description/urdf/revo2_right_hand.urdf"
            echo "✓ Using Revo2 Hand URDF"
            ;;
        2)
            URDF_PATH="brainco_hand/brainco_right.urdf"
            echo "✓ Using BrainCo Hand URDF"
            ;;
        *)
            echo "Invalid choice. Using BrainCo Hand."
            URDF_PATH="brainco_hand/brainco_right.urdf"
            ;;
    esac
}

# Function to select hand side
select_hand() {
    read -p "Hand side [left/right] (default: right): " hand_side
    hand_side=${hand_side:-right}
    echo "✓ Using $hand_side hand"
}

# Main menu
echo "Select input mode:"
echo "  1) Single image"
echo "  2) Image folder (sequence)"
echo "  3) Image list (multiple files)"
echo ""
read -p "Enter choice [1-3]: " mode

select_urdf
select_hand

case $mode in
    1)
        # Single image mode
        echo ""
        echo "=============================================="
        echo "  Single Image Mode"
        echo "=============================================="
        read -p "Enter image path: " image_path
        
        if [ ! -f "$image_path" ]; then
            echo "Error: Image file not found: $image_path"
            exit 1
        fi
        
        echo ""
        echo "Processing single image..."
        python3 image_retargeting.py \
            --image "$image_path" \
            --urdf "$URDF_PATH" \
            --hand "$hand_side"
        ;;
        
    2)
        # Image folder mode
        echo ""
        echo "=============================================="
        echo "  Image Folder Mode"
        echo "=============================================="
        read -p "Enter folder path: " folder_path
        
        if [ ! -d "$folder_path" ]; then
            echo "Error: Folder not found: $folder_path"
            exit 1
        fi
        
        read -p "Image pattern (default: *.jpg): " pattern
        pattern=${pattern:-*.jpg}
        
        read -p "FPS for trajectory (default: 30): " fps
        fps=${fps:-30}
        
        read -p "Save annotated images? [y/n] (default: n): " save_annotated
        
        if [[ "$save_annotated" == "y" ]]; then
            read -p "Output folder (default: annotated_images): " output_folder
            output_folder=${output_folder:-annotated_images}
            OUTPUT_ARG="--output $output_folder"
        else
            OUTPUT_ARG=""
        fi
        
        echo ""
        echo "Processing image sequence..."
        python3 image_retargeting.py \
            --folder "$folder_path" \
            --urdf "$URDF_PATH" \
            --hand "$hand_side" \
            --pattern "$pattern" \
            --fps "$fps" \
            $OUTPUT_ARG
        ;;
        
    3)
        # Image list mode
        echo ""
        echo "=============================================="
        echo "  Image List Mode"
        echo "=============================================="
        echo "Enter image paths (one per line, empty line to finish):"
        
        image_list=()
        while true; do
            read -p "> " img_path
            if [ -z "$img_path" ]; then
                break
            fi
            if [ -f "$img_path" ]; then
                image_list+=("$img_path")
                echo "  ✓ Added: $img_path"
            else
                echo "  ✗ File not found: $img_path"
            fi
        done
        
        if [ ${#image_list[@]} -eq 0 ]; then
            echo "Error: No valid images provided"
            exit 1
        fi
        
        read -p "FPS for trajectory (default: 30): " fps
        fps=${fps:-30}
        
        echo ""
        echo "Processing ${#image_list[@]} images..."
        python3 image_retargeting.py \
            --list "${image_list[@]}" \
            --urdf "$URDF_PATH" \
            --hand "$hand_side" \
            --fps "$fps"
        ;;
        
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "=============================================="
echo "  Complete!"
echo "=============================================="
