#!/usr/bin/env python3
"""
Realtime hand retargeting visualizer.

Opens either a webcam or a video file, detects the requested human hand with
MediaPipe, retargets it to the BrainCo/Revo2 URDF, and shows both views in one
window in realtime.
"""

import argparse
import json
import platform
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

from hand_retargeting import Revo2HandRetargeting
from render_hand_poses import HandPoseRenderer


class RealtimeRetargetingVisualizer:
    """Realtime camera/video visualization for detection plus retargeted hand."""

    def __init__(
        self,
        urdf_path: str,
        hand_side: str = "right",
        camera_index: int = 0,
        camera_width: int = 1280,
        camera_height: int = 720,
        camera_fps: float = 30.0,
        render_width: int = 640,
        render_height: int = 480,
        robot_panel_offset_y: int = 30,
        mirror: bool = True,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ):
        self.urdf_path = urdf_path
        self.hand_side = hand_side
        self.camera_index = camera_index
        self.camera_width = camera_width
        self.camera_height = camera_height
        self.camera_fps = camera_fps
        self.render_width = render_width
        self.render_height = render_height
        self.robot_panel_offset_y = robot_panel_offset_y
        self.mirror = mirror
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        self.retargeting = Revo2HandRetargeting(urdf_path, hand_side)
        self.renderer = HandPoseRenderer(urdf_path, width=render_width, height=render_height)

    def _open_capture(self, video_path: Optional[str]) -> Tuple[cv2.VideoCapture, str]:
        """Open a video file or camera source with backend fallback on macOS."""
        if video_path:
            capture = cv2.VideoCapture(video_path)
            if not capture.isOpened():
                raise RuntimeError(f"Could not open video source: {video_path}")
            return capture, f"video: {video_path}"

        backend_candidates: List[Tuple[str, Optional[int]]] = []
        if platform.system() == "Darwin" and hasattr(cv2, "CAP_AVFOUNDATION"):
            backend_candidates.append(("AVFoundation", cv2.CAP_AVFOUNDATION))
        if hasattr(cv2, "CAP_ANY"):
            backend_candidates.append(("CAP_ANY", cv2.CAP_ANY))
        backend_candidates.append(("default", None))

        for backend_name, backend in backend_candidates:
            if backend is None:
                capture = cv2.VideoCapture(self.camera_index)
            else:
                capture = cv2.VideoCapture(self.camera_index, backend)

            if capture.isOpened():
                capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
                capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
                capture.set(cv2.CAP_PROP_FPS, self.camera_fps)
                return capture, f"camera {self.camera_index} ({backend_name})"

            capture.release()

        raise RuntimeError(
            f"Could not open camera index {self.camera_index}. "
            "On macOS, check Camera permissions for the terminal/Python process."
        )

    def _resolve_actual_hand(self, mediapipe_label: str) -> str:
        """
        Convert MediaPipe's camera-perspective handedness to the actual hand side.
        """
        label = mediapipe_label.lower()
        if label == "left":
            return "right"
        if label == "right":
            return "left"
        return label

    def _select_target_hand(self, results) -> Tuple[Optional[object], Optional[object]]:
        """Pick the highest-confidence detected hand matching the requested side."""
        if not results.multi_hand_landmarks or not results.multi_handedness:
            return None, None

        best_score = -1.0
        best_landmarks = None
        best_handedness = None

        for landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            classification = handedness.classification[0]
            actual_hand = self._resolve_actual_hand(classification.label)
            if actual_hand != self.hand_side:
                continue
            if classification.score > best_score:
                best_score = classification.score
                best_landmarks = landmarks
                best_handedness = handedness

        return best_landmarks, best_handedness

    def _summarize_detected_hands(self, results) -> str:
        """Format a short summary of currently detected hands."""
        if not results.multi_handedness:
            return "none"

        detected = []
        for handedness in results.multi_handedness:
            classification = handedness.classification[0]
            actual_hand = self._resolve_actual_hand(classification.label).upper()
            detected.append(f"{actual_hand} {classification.score:.2f}")
        return ", ".join(detected)

    def _resize_and_pad(self, image: np.ndarray, target_width: int, target_height: int) -> np.ndarray:
        """Resize while preserving aspect ratio and pad to target size."""
        src_height, src_width = image.shape[:2]
        if src_height == 0 or src_width == 0:
            return np.zeros((target_height, target_width, 3), dtype=np.uint8)

        scale = min(target_width / src_width, target_height / src_height)
        resized_width = max(1, int(src_width * scale))
        resized_height = max(1, int(src_height * scale))

        resized = cv2.resize(image, (resized_width, resized_height))
        canvas = np.full((target_height, target_width, 3), 18, dtype=np.uint8)

        offset_x = (target_width - resized_width) // 2
        offset_y = (target_height - resized_height) // 2
        canvas[offset_y:offset_y + resized_height, offset_x:offset_x + resized_width] = resized
        return canvas

    def _draw_header(self, panel: np.ndarray, title: str, subtitle: str) -> None:
        """Draw a compact panel header."""
        cv2.rectangle(panel, (0, 0), (panel.shape[1], 42), (34, 34, 34), -1)
        cv2.putText(
            panel,
            title,
            (12, 18),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )
        cv2.putText(
            panel,
            subtitle,
            (12, 36),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (190, 190, 190),
            1,
            cv2.LINE_AA,
        )

    def _draw_lines(
        self,
        panel: np.ndarray,
        lines: List[str],
        start_y: int = 60,
        color: Tuple[int, int, int] = (0, 255, 0),
    ) -> None:
        """Draw a list of text lines with consistent spacing."""
        y = start_y
        for line in lines:
            cv2.putText(
                panel,
                line,
                (12, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.48,
                color,
                1,
                cv2.LINE_AA,
            )
            y += 20

    def _render_robot_panel(self, joint_angles: Optional[Dict[str, float]]) -> np.ndarray:
        """Render the retargeted BrainCo hand and annotate controllable joints."""
        if joint_angles is not None:
            self.renderer.set_joint_angles(joint_angles, in_degrees=False)

        render_rgb = self.renderer.render()
        panel = cv2.cvtColor(render_rgb, cv2.COLOR_RGB2BGR)
        if self.robot_panel_offset_y:
            shift_matrix = np.float32([[1, 0, 0], [0, 1, self.robot_panel_offset_y]])
            panel = cv2.warpAffine(
                panel,
                shift_matrix,
                (panel.shape[1], panel.shape[0]),
                borderMode=cv2.BORDER_REPLICATE,
            )
        self._draw_header(
            panel,
            "Retargeted BrainCo Hand",
            f"{self.hand_side.upper()} hand | URDF: {Path(self.urdf_path).name}",
        )

        if joint_angles is None:
            self._draw_lines(panel, ["No matching hand detected"], start_y=72, color=(0, 165, 255))
            return panel

        lines = []
        for key, joint_name in self.retargeting.controllable_joints.items():
            angle_deg = np.degrees(joint_angles[joint_name])
            short_name = key.replace("_proximal", "").replace("_metacarpal", "_meta")
            lines.append(f"{short_name}: {angle_deg:6.1f} deg")

        self._draw_lines(panel, lines, start_y=72, color=(0, 255, 0))
        return panel

    def _render_camera_panel(
        self,
        frame: np.ndarray,
        source_label: str,
        display_fps: float,
        frame_idx: int,
        target_found: bool,
        detected_summary: str,
        handedness,
        paused: bool,
    ) -> np.ndarray:
        """Prepare the camera/MediaPipe panel."""
        display_frame = cv2.flip(frame, 1) if self.mirror else frame
        panel = self._resize_and_pad(display_frame, self.render_width, self.render_height)

        status = "target matched" if target_found else "waiting for target hand"
        self._draw_header(panel, "Detected Hand Model", f"{source_label} | {status}")

        lines = [
            f"frame: {frame_idx}",
            f"display fps: {display_fps:5.1f}",
            f"target hand: {self.hand_side.upper()}",
            f"detected hands: {detected_summary}",
            f"mirror: {'on' if self.mirror else 'off'}",
            "controls: q quit | space pause | m mirror",
        ]

        if handedness is not None:
            classification = handedness.classification[0]
            actual_hand = self._resolve_actual_hand(classification.label).upper()
            lines.insert(3, f"matched hand: {actual_hand} {classification.score:.2f}")

        if paused:
            lines.insert(0, "paused")

        color = (0, 255, 0) if target_found else (0, 165, 255)
        self._draw_lines(panel, lines, start_y=72, color=color)
        return panel

    def run(
        self,
        video_path: Optional[str] = None,
        trajectory_out: Optional[str] = None,
        max_frames: Optional[int] = None,
        headless: bool = False,
    ) -> Optional[Dict]:
        """
        Run realtime visualization from a camera or video source.

        Returns the collected trajectory if `trajectory_out` is provided, otherwise `None`.
        """
        capture, source_label = self._open_capture(video_path)

        source_fps = capture.get(cv2.CAP_PROP_FPS)
        if not source_fps or np.isnan(source_fps) or source_fps <= 1e-6:
            source_fps = self.camera_fps

        trajectory = None
        if trajectory_out:
            trajectory = {
                "fps": source_fps,
                "angle_unit": "degrees",
                "source": "video" if video_path else "camera",
                "hand": self.hand_side,
                "frames": [],
            }

        print(f"\n{'=' * 72}")
        print("Realtime Hand Retargeting")
        print(f"{'=' * 72}")
        print(f"Source: {source_label}")
        print(f"Target hand: {self.hand_side}")
        print(f"Render size: {self.render_width}x{self.render_height}")
        print("Controls: q quit | SPACE pause/resume | m mirror")
        if trajectory_out:
            print(f"Trajectory output: {trajectory_out}")
        if headless:
            print("Headless mode: enabled")
        print(f"{'=' * 72}\n")

        last_combined = None
        frame_idx = 0
        paused = False
        last_frame_time = time.perf_counter()
        session_start_time = time.perf_counter()

        with self.retargeting.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence,
        ) as hands:
            try:
                while capture.isOpened():
                    if not paused:
                        success, frame = capture.read()
                        if not success:
                            break

                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        rgb_frame.flags.writeable = False
                        results = hands.process(rgb_frame)
                        rgb_frame.flags.writeable = True
                        annotated_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

                        if results.multi_hand_landmarks:
                            for hand_landmarks in results.multi_hand_landmarks:
                                self.retargeting.mp_drawing.draw_landmarks(
                                    annotated_frame,
                                    hand_landmarks,
                                    self.retargeting.mp_hands.HAND_CONNECTIONS,
                                    self.retargeting.mp_drawing_styles.get_default_hand_landmarks_style(),
                                    self.retargeting.mp_drawing_styles.get_default_hand_connections_style(),
                                )

                        target_landmarks, target_handedness = self._select_target_hand(results)
                        joint_angles = None

                        if target_landmarks is not None:
                            joint_angles = self.retargeting.retarget_hand_pose(target_landmarks.landmark)

                        detected_summary = self._summarize_detected_hands(results)
                        now = time.perf_counter()
                        display_fps = 1.0 / max(now - last_frame_time, 1e-6)
                        last_frame_time = now

                        camera_panel = self._render_camera_panel(
                            frame=annotated_frame,
                            source_label=source_label,
                            display_fps=display_fps,
                            frame_idx=frame_idx,
                            target_found=joint_angles is not None,
                            detected_summary=detected_summary,
                            handedness=target_handedness,
                            paused=paused,
                        )
                        robot_panel = self._render_robot_panel(joint_angles)
                        last_combined = np.hstack((camera_panel, robot_panel))

                        if trajectory is not None:
                            joint_angles_deg = None
                            if joint_angles is not None:
                                joint_angles_deg = {k: float(np.degrees(v)) for k, v in joint_angles.items()}
                            if video_path:
                                timestamp = frame_idx / source_fps
                            else:
                                timestamp = time.perf_counter() - session_start_time
                            trajectory["frames"].append(
                                {
                                    "frame": frame_idx,
                                    "timestamp": timestamp,
                                    "joint_angles": joint_angles_deg,
                                }
                            )

                        frame_idx += 1

                    if not headless and last_combined is not None:
                        cv2.imshow("Realtime Hand Retargeting", last_combined)
                        key = cv2.waitKey(1) & 0xFF
                    else:
                        key = -1
                        time.sleep(0.001)

                    if key == ord("q"):
                        break
                    if key == ord(" "):
                        paused = not paused
                    if key == ord("m"):
                        self.mirror = not self.mirror

                    if max_frames is not None and frame_idx >= max_frames:
                        break

            finally:
                capture.release()
                if not headless:
                    cv2.destroyAllWindows()

        print(f"Processed {frame_idx} frame(s).")

        if trajectory is not None:
            trajectory_path = Path(trajectory_out)
            trajectory_path.parent.mkdir(parents=True, exist_ok=True)

            with trajectory_path.open("w") as handle:
                json.dump(trajectory, handle, indent=2)

            controllable_trajectory = self.retargeting._extract_controllable_trajectory(trajectory)
            controllable_path = trajectory_path.with_name(
                f"{trajectory_path.stem}_6dof{trajectory_path.suffix}"
            )
            with controllable_path.open("w") as handle:
                json.dump(controllable_trajectory, handle, indent=2)

            print(f"Saved trajectory: {trajectory_path}")
            print(f"Saved 6-DOF trajectory: {controllable_path}")

        return trajectory

    def close(self) -> None:
        """Release the PyBullet renderer."""
        self.renderer.cleanup()


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Realtime webcam/video hand retargeting with BrainCo visualization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Realtime webcam on macOS
  python realtime_visualize.py \
      --camera-index 0 \
      --urdf brainco_hand/brainco_right.urdf \
      --hand right

  # Run against a saved video
  python realtime_visualize.py \
      --video human_hand_video.mp4 \
      --urdf brainco_hand/brainco_right.urdf \
      --hand right

  # Headless smoke test
  python realtime_visualize.py \
      --video human_hand_video.mp4 \
      --urdf brainco_hand/brainco_right.urdf \
      --hand right \
      --headless \
      --max-frames 30 \
      --trajectory-out /tmp/realtime_test.json
        """,
    )

    parser.add_argument("--video", type=str, default=None, help="Optional input video file.")
    parser.add_argument(
        "--camera-index",
        type=int,
        default=0,
        help="Camera index for live capture (default: 0).",
    )
    parser.add_argument("--urdf", type=str, required=True, help="Path to the BrainCo/Revo2 URDF.")
    parser.add_argument(
        "--hand",
        type=str,
        default="right",
        choices=["right", "left"],
        help="Actual hand side to track.",
    )
    parser.add_argument(
        "--camera-width",
        type=int,
        default=1280,
        help="Requested camera width for webcam mode.",
    )
    parser.add_argument(
        "--camera-height",
        type=int,
        default=720,
        help="Requested camera height for webcam mode.",
    )
    parser.add_argument(
        "--camera-fps",
        type=float,
        default=30.0,
        help="Fallback FPS when the source does not report one.",
    )
    parser.add_argument(
        "--render-width",
        type=int,
        default=640,
        help="Width of each output panel.",
    )
    parser.add_argument(
        "--render-height",
        type=int,
        default=480,
        help="Height of each output panel.",
    )
    parser.add_argument(
        "--robot-panel-offset-y",
        type=int,
        default=30,
        help="Shift the rendered robot-hand panel downward by this many pixels.",
    )
    parser.add_argument(
        "--no-mirror",
        action="store_true",
        help="Disable mirrored preview for the camera panel.",
    )
    parser.add_argument(
        "--min-detection-confidence",
        type=float,
        default=0.5,
        help="MediaPipe detection confidence threshold.",
    )
    parser.add_argument(
        "--min-tracking-confidence",
        type=float,
        default=0.5,
        help="MediaPipe tracking confidence threshold.",
    )
    parser.add_argument(
        "--trajectory-out",
        type=str,
        default=None,
        help="Optional path to save the recorded trajectory JSON.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Optional frame limit, useful for tests.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Process frames without opening an OpenCV window.",
    )
    return parser


def main() -> None:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args()

    visualizer = RealtimeRetargetingVisualizer(
        urdf_path=args.urdf,
        hand_side=args.hand,
        camera_index=args.camera_index,
        camera_width=args.camera_width,
        camera_height=args.camera_height,
        camera_fps=args.camera_fps,
        render_width=args.render_width,
        render_height=args.render_height,
        robot_panel_offset_y=args.robot_panel_offset_y,
        mirror=not args.no_mirror,
        min_detection_confidence=args.min_detection_confidence,
        min_tracking_confidence=args.min_tracking_confidence,
    )

    try:
        visualizer.run(
            video_path=args.video,
            trajectory_out=args.trajectory_out,
            max_frames=args.max_frames,
            headless=args.headless,
        )
    finally:
        visualizer.close()


if __name__ == "__main__":
    main()
