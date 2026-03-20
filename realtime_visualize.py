#!/usr/bin/env python3
"""
Realtime hand retargeting visualizer.

Opens either a webcam or a video file, detects the requested human hand(s) with
MediaPipe, retargets them to the BrainCo/Revo2 URDF(s), and shows both views in
one window in realtime.
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
    """Realtime camera/video visualization for detection plus retargeted hand(s)."""

    def __init__(
        self,
        urdf_path: Optional[str] = None,
        hand_side: str = "right",
        left_urdf_path: Optional[str] = None,
        right_urdf_path: Optional[str] = None,
        camera_index: int = 0,
        camera_width: int = 1280,
        camera_height: int = 720,
        camera_fps: float = 30.0,
        render_width: int = 640,
        render_height: int = 720,
        robot_panel_offset_y: int = 30,
        mirror: bool = True,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ):
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
        self.window_name = "Realtime Hand Retargeting"

        self.active_hands = ["left", "right"] if hand_side == "both" else [hand_side]
        self.urdf_paths = self._resolve_urdf_paths(urdf_path, left_urdf_path, right_urdf_path)

        self.retargeters: Dict[str, Revo2HandRetargeting] = {}
        self.renderers: Dict[str, HandPoseRenderer] = {}
        for side in self.active_hands:
            self.retargeters[side] = Revo2HandRetargeting(self.urdf_paths[side], side)
            self.renderers[side] = HandPoseRenderer(
                self.urdf_paths[side],
                width=render_width,
                height=render_height,
            )

        # Preserve the single-hand attributes used elsewhere in the file.
        self.urdf_path = self.urdf_paths[self.active_hands[0]]
        self.retargeting = self.retargeters[self.active_hands[0]]
        self.renderer = self.renderers[self.active_hands[0]]

    def _resolve_urdf_paths(
        self,
        urdf_path: Optional[str],
        left_urdf_path: Optional[str],
        right_urdf_path: Optional[str],
    ) -> Dict[str, str]:
        """Resolve the URDF path(s) required for the selected hand mode."""
        if self.hand_side in {"left", "right"}:
            if self.hand_side == "left":
                resolved = urdf_path or left_urdf_path
            else:
                resolved = urdf_path or right_urdf_path
            if not resolved:
                raise ValueError("Single-hand mode requires --urdf.")
            return {self.hand_side: str(Path(resolved))}

        resolved_left = Path(left_urdf_path).expanduser() if left_urdf_path else None
        resolved_right = Path(right_urdf_path).expanduser() if right_urdf_path else None

        if urdf_path:
            base_path = Path(urdf_path).expanduser()
            base_name = base_path.name.lower()
            if "left" in base_name and resolved_left is None:
                resolved_left = base_path
                candidate = base_path.with_name(base_path.name.replace("left", "right"))
                if candidate.exists():
                    resolved_right = resolved_right or candidate
            elif "right" in base_name and resolved_right is None:
                resolved_right = base_path
                candidate = base_path.with_name(base_path.name.replace("right", "left"))
                if candidate.exists():
                    resolved_left = resolved_left or candidate

        if resolved_left is None or resolved_right is None:
            default_dir = Path(__file__).resolve().parent / "brainco_hand"
            default_left = default_dir / "brainco_left.urdf"
            default_right = default_dir / "brainco_right.urdf"
            if resolved_left is None and default_left.exists():
                resolved_left = default_left
            if resolved_right is None and default_right.exists():
                resolved_right = default_right

        missing = []
        if resolved_left is None or not resolved_left.exists():
            missing.append("left")
        if resolved_right is None or not resolved_right.exists():
            missing.append("right")
        if missing:
            raise ValueError(
                "Both-hand mode requires valid left and right URDFs. "
                "Pass --left-urdf and --right-urdf, or provide --urdf that points "
                f"to one side with the sibling file present. Missing: {', '.join(missing)}"
            )

        return {
            "left": str(resolved_left),
            "right": str(resolved_right),
        }

    def _camera_stream_ready(self, capture: cv2.VideoCapture, attempts: int = 20, delay_s: float = 0.1) -> bool:
        """Warm up a live camera and verify that it can actually deliver frames."""
        for _ in range(attempts):
            success, frame = capture.read()
            if success and frame is not None and frame.size > 0:
                return True
            time.sleep(delay_s)
        return False

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

        backend_failures = []
        for backend_name, backend in backend_candidates:
            if backend is None:
                capture = cv2.VideoCapture(self.camera_index)
            else:
                capture = cv2.VideoCapture(self.camera_index, backend)

            if not capture.isOpened():
                backend_failures.append(f"{backend_name}: open failed")
                capture.release()
                continue

            capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
            capture.set(cv2.CAP_PROP_FPS, self.camera_fps)

            if self._camera_stream_ready(capture):
                return capture, f"camera {self.camera_index} ({backend_name})"

            backend_failures.append(f"{backend_name}: opened but produced no frames")
            capture.release()

        raise RuntimeError(
            f"Could not open camera index {self.camera_index}. "
            "On macOS, check Camera permissions for the terminal/Python process. "
            f"Tried backends: {', '.join(backend_failures)}"
        )

    def _resolve_actual_hand(self, mediapipe_label: str) -> str:
        """Convert MediaPipe's camera-perspective handedness to the actual hand side."""
        label = mediapipe_label.lower()
        if label == "left":
            return "right"
        if label == "right":
            return "left"
        return label

    def _select_target_hands(self, results) -> Dict[str, Tuple[Optional[object], Optional[object]]]:
        """Pick the highest-confidence detection for each requested actual hand."""
        selected = {side: (None, None) for side in self.active_hands}
        best_scores = {side: -1.0 for side in self.active_hands}

        if not results.multi_hand_landmarks or not results.multi_handedness:
            return selected

        for landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            classification = handedness.classification[0]
            actual_hand = self._resolve_actual_hand(classification.label)
            if actual_hand not in selected:
                continue
            if classification.score > best_scores[actual_hand]:
                best_scores[actual_hand] = classification.score
                selected[actual_hand] = (landmarks, handedness)

        return selected

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

    def _render_robot_panel(self, side: str, joint_angles: Optional[Dict[str, float]]) -> np.ndarray:
        """Render one retargeted BrainCo hand and annotate controllable joints."""
        renderer = self.renderers[side]
        retargeter = self.retargeters[side]

        if joint_angles is not None:
            renderer.set_joint_angles(joint_angles, in_degrees=False)

        render_rgb = renderer.render()
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
            f"{side.upper()} BrainCo Hand",
            f"URDF: {Path(self.urdf_paths[side]).name}",
        )

        if joint_angles is None:
            self._draw_lines(panel, [f"No {side} hand detected"], start_y=72, color=(0, 165, 255))
            return panel

        lines = []
        for key, joint_name in retargeter.controllable_joints.items():
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
        detected_summary: str,
        selected_hands: Dict[str, Tuple[Optional[object], Optional[object]]],
        joint_angles_by_side: Dict[str, Optional[Dict[str, float]]],
        paused: bool,
    ) -> np.ndarray:
        """Prepare the camera/MediaPipe panel."""
        display_frame = cv2.flip(frame, 1) if self.mirror else frame
        panel = self._resize_and_pad(display_frame, self.render_width, self.render_height)

        if self.hand_side == "both":
            left_found = joint_angles_by_side["left"] is not None
            right_found = joint_angles_by_side["right"] is not None
            status = f"L {'ok' if left_found else '--'} | R {'ok' if right_found else '--'}"
            subtitle = f"{source_label} | {status}"
        else:
            target_found = joint_angles_by_side[self.hand_side] is not None
            status = "target matched" if target_found else "waiting for target hand"
            subtitle = f"{source_label} | {status}"

        self._draw_header(panel, "Detected Hand Model", subtitle)

        lines = [
            f"frame: {frame_idx}",
            f"display fps: {display_fps:5.1f}",
            f"target hand: {self.hand_side.upper()}",
            f"detected hands: {detected_summary}",
            f"mirror: {'on' if self.mirror else 'off'}",
            "controls: q quit | space pause | m mirror",
        ]

        for side in self.active_hands:
            _, handedness = selected_hands[side]
            if handedness is None:
                lines.insert(3, f"{side.upper()} match: none")
                continue
            classification = handedness.classification[0]
            actual_hand = self._resolve_actual_hand(classification.label).upper()
            score_text = f"{actual_hand} {classification.score:.2f}"
            lines.insert(3, f"{side.upper()} match: {score_text}")

        if paused:
            lines.insert(0, "paused")

        any_found = any(joint_angles_by_side[side] is not None for side in self.active_hands)
        color = (0, 255, 0) if any_found else (0, 165, 255)
        self._draw_lines(panel, lines, start_y=72, color=color)
        return panel

    def _extract_both_controllable_trajectory(self, full_trajectory: Dict) -> Dict:
        """Extract the 6-DOF controllable joints for both hands."""
        hands_meta = {}
        for side in ("left", "right"):
            retargeter = self.retargeters[side]
            hands_meta[side] = {
                "dof": 6,
                "joints": list(retargeter.controllable_joints.keys()),
                "joint_names": list(retargeter.controllable_joints.values()),
                "mimic_info": retargeter.mimic_joints,
            }

        controllable = {
            "fps": full_trajectory["fps"],
            "angle_unit": "degrees",
            "hand": "both",
            "hands": hands_meta,
            "frames": [],
        }

        for frame in full_trajectory["frames"]:
            frame_out = {
                "frame": frame["frame"],
                "timestamp": frame["timestamp"],
                "left_joint_angles": None,
                "right_joint_angles": None,
            }
            for side in ("left", "right"):
                side_angles = frame.get(f"{side}_joint_angles")
                if side_angles:
                    frame_out[f"{side}_joint_angles"] = {
                        joint_name: side_angles[joint_name]
                        for joint_name in self.retargeters[side].controllable_joints.values()
                        if joint_name in side_angles
                    }
            controllable["frames"].append(frame_out)

        return controllable

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
        if self.hand_side == "both":
            print(f"Left URDF: {self.urdf_paths['left']}")
            print(f"Right URDF: {self.urdf_paths['right']}")
            print("Display layout: scene | left retargeting | right retargeting")
        else:
            print(f"URDF: {self.urdf_path}")
        print(f"Render size: {self.render_width}x{self.render_height}")
        print("Controls: q quit | SPACE pause/resume | m mirror")
        if trajectory_out:
            print(f"Trajectory output: {trajectory_out}")
        if headless:
            print("Headless mode: enabled")
        print(f"{'=' * 72}\n")

        if not headless:
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(
                self.window_name,
                self.render_width * (1 + len(self.active_hands)),
                self.render_height,
            )

        last_combined = None
        frame_idx = 0
        paused = False
        last_frame_time = time.perf_counter()
        session_start_time = time.perf_counter()
        consecutive_read_failures = 0

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
                            consecutive_read_failures += 1
                            if not video_path and consecutive_read_failures < 10:
                                time.sleep(0.05)
                                continue
                            raise RuntimeError(
                                "Camera/video source stopped delivering frames. "
                                "Try another --camera-index on macOS if this is a live camera."
                            )
                        consecutive_read_failures = 0

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

                        selected_hands = self._select_target_hands(results)
                        joint_angles_by_side: Dict[str, Optional[Dict[str, float]]] = {
                            side: None for side in self.active_hands
                        }
                        for side in self.active_hands:
                            landmarks, _ = selected_hands[side]
                            if landmarks is not None:
                                joint_angles_by_side[side] = self.retargeters[side].retarget_hand_pose(
                                    landmarks.landmark
                                )

                        detected_summary = self._summarize_detected_hands(results)
                        now = time.perf_counter()
                        display_fps = 1.0 / max(now - last_frame_time, 1e-6)
                        last_frame_time = now

                        camera_panel = self._render_camera_panel(
                            frame=annotated_frame,
                            source_label=source_label,
                            display_fps=display_fps,
                            frame_idx=frame_idx,
                            detected_summary=detected_summary,
                            selected_hands=selected_hands,
                            joint_angles_by_side=joint_angles_by_side,
                            paused=paused,
                        )
                        robot_panels = [
                            self._render_robot_panel(side, joint_angles_by_side[side])
                            for side in self.active_hands
                        ]
                        last_combined = np.hstack([camera_panel] + robot_panels)

                        if trajectory is not None:
                            if video_path:
                                timestamp = frame_idx / source_fps
                            else:
                                timestamp = time.perf_counter() - session_start_time

                            if self.hand_side == "both":
                                frame_record = {
                                    "frame": frame_idx,
                                    "timestamp": timestamp,
                                    "left_joint_angles": None,
                                    "right_joint_angles": None,
                                }
                                for side in ("left", "right"):
                                    side_angles = joint_angles_by_side[side]
                                    if side_angles is not None:
                                        frame_record[f"{side}_joint_angles"] = {
                                            k: float(np.degrees(v)) for k, v in side_angles.items()
                                        }
                            else:
                                side_angles = joint_angles_by_side[self.hand_side]
                                frame_record = {
                                    "frame": frame_idx,
                                    "timestamp": timestamp,
                                    "joint_angles": None,
                                }
                                if side_angles is not None:
                                    frame_record["joint_angles"] = {
                                        k: float(np.degrees(v)) for k, v in side_angles.items()
                                    }

                            trajectory["frames"].append(frame_record)

                        frame_idx += 1

                    if not headless and last_combined is not None:
                        cv2.imshow(self.window_name, last_combined)
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

            if self.hand_side == "both":
                controllable_trajectory = self._extract_both_controllable_trajectory(trajectory)
            else:
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
        """Release the PyBullet renderer(s)."""
        for renderer in self.renderers.values():
            renderer.cleanup()


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser."""
    parser = argparse.ArgumentParser(
        description="Realtime webcam/video hand retargeting with BrainCo visualization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Realtime webcam for a single hand
  python realtime_visualize.py \
      --camera-index 0 \
      --urdf brainco_hand/brainco_right.urdf \
      --hand right

  # Realtime webcam for both hands
  python realtime_visualize.py \
      --camera-index 0 \
      --hand both \
      --left-urdf brainco_hand/brainco_left.urdf \
      --right-urdf brainco_hand/brainco_right.urdf

  # Run against a saved video
  python realtime_visualize.py \
      --video human_hand_video.mp4 \
      --urdf brainco_hand/brainco_right.urdf \
      --hand right

  # Headless smoke test for both hands
  python realtime_visualize.py \
      --video human_hand_video.mp4 \
      --hand both \
      --left-urdf brainco_hand/brainco_left.urdf \
      --right-urdf brainco_hand/brainco_right.urdf \
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
    parser.add_argument(
        "--urdf",
        type=str,
        default=None,
        help="Path to the BrainCo/Revo2 URDF. Required for single-hand mode.",
    )
    parser.add_argument(
        "--left-urdf",
        type=str,
        default=None,
        help="Optional left-hand URDF path, used for --hand both.",
    )
    parser.add_argument(
        "--right-urdf",
        type=str,
        default=None,
        help="Optional right-hand URDF path, used for --hand both.",
    )
    parser.add_argument(
        "--hand",
        type=str,
        default="right",
        choices=["right", "left", "both"],
        help="Actual hand side(s) to track.",
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
        default=720,
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
        left_urdf_path=args.left_urdf,
        right_urdf_path=args.right_urdf,
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
