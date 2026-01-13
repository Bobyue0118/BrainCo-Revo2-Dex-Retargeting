#!/usr/bin/env python3
"""
Test script to verify hand detection label flipping
"""

import cv2
import mediapipe as mp
import sys

def test_hand_detection(image_path):
    """Test MediaPipe hand detection and label."""
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read image {image_path}")
        return
    
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    print(f"\n{'='*60}")
    print(f"Testing: {image_path}")
    print(f"{'='*60}")
    
    # Detect hands
    with mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=2,
        min_detection_confidence=0.5
    ) as hands:
        results = hands.process(image_rgb)
        
        if results.multi_hand_landmarks and results.multi_handedness:
            print(f"\nDetected {len(results.multi_hand_landmarks)} hand(s):")
            
            for idx, (hand_landmarks, handedness) in enumerate(zip(
                results.multi_hand_landmarks, 
                results.multi_handedness
            )):
                label = handedness.classification[0].label
                score = handedness.classification[0].score
                
                print(f"\nHand {idx + 1}:")
                print(f"  MediaPipe label: {label}")
                print(f"  Confidence: {score:.2f}")
                
                # Determine actual hand side (flipped)
                if label.lower() == 'left':
                    actual = 'RIGHT'
                else:
                    actual = 'LEFT'
                
                print(f"  Actual hand side: {actual} (mirrored)")
                
                # Draw landmarks
                annotated = image.copy()
                mp_drawing.draw_landmarks(
                    annotated,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )
                
                # Add label
                h, w = annotated.shape[:2]
                cv2.putText(annotated, f"MediaPipe: {label}", 
                          (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(annotated, f"Actual: {actual}", 
                          (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Save annotated image
                output_path = f"test_detection_{idx}.jpg"
                cv2.imwrite(output_path, annotated)
                print(f"  Saved annotated image: {output_path}")
        else:
            print("\n✗ No hands detected")
    
    print(f"\n{'='*60}\n")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_hand_detection.py <image_path>")
        print("Example: python test_hand_detection.py tray/23.png")
        sys.exit(1)
    
    test_hand_detection(sys.argv[1])
"""Test MediaPipe hand detection to see which label it returns"""

import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Test with first image
print("Testing tray/23.png...")
image = cv2.imread('tray/23.png')
if image is None:
    print("Could not read image!")
    exit(1)

height, width = image.shape[:2]
print(f"Image size: {width}x{height}")

image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

with mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=2,
    min_detection_confidence=0.5
) as hands:
    results = hands.process(image_rgb)
    
    if results.multi_hand_landmarks and results.multi_handedness:
        print(f"\nDetected {len(results.multi_hand_landmarks)} hand(s):")
        for idx, handedness in enumerate(results.multi_handedness):
            label = handedness.classification[0].label
            score = handedness.classification[0].score
            print(f"  Hand {idx}: MediaPipe label = '{label}' (confidence {score:.2%})")
            
            # Draw on image
            hand_landmarks = results.multi_hand_landmarks[idx]
            mp_drawing.draw_landmarks(
                image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )
            
            # Add text label
            cv2.putText(image, f"MediaPipe: {label}", (10, 30 + idx*30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Save annotated image
        cv2.imwrite('test_hand_detection_result.jpg', image)
        print(f"\nAnnotated image saved to: test_hand_detection_result.jpg")
        print("\nNote: MediaPipe's 'Right'/'Left' labels can be confusing:")
        print("  - For selfie/mirror images: labels are from YOUR perspective")
        print("  - For photos of others: labels are from THEIR perspective")
        print("  - This is actually the person's anatomical right/left hand")
    else:
        print("No hands detected!")
