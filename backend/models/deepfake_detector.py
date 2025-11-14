import cv2
import numpy as np
from typing import Dict
import os


class DeepfakeDetector:
    """
    Lightweight video deepfake detection using computer vision analysis
    Detects: Face swap, lip sync, face reenactment
    Note: This is a demonstration version. For production, integrate trained ML models.
    """

    def __init__(self):
        # Load OpenCV's pre-trained face detector
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    async def analyze_video(self, video_path: str) -> Dict:
        """
        Analyze video for deepfake manipulation
        Returns detailed analysis with confidence scores
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise Exception("Could not open video file")

            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            if frame_count == 0 or fps == 0:
                raise Exception("Invalid video file")

            # Sample frames for analysis
            sample_rate = max(1, frame_count // 30)  # Analyze ~30 frames
            frames_analyzed = 0
            anomaly_scores = []
            face_inconsistencies = []
            compression_artifacts = []

            frame_idx = 0
            prev_frame_gray = None

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_idx % sample_rate == 0:
                    # Convert to grayscale for analysis
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                    # Detect faces
                    faces = self.face_cascade.detectMultiScale(
                        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                    )

                    if len(faces) > 0:
                        for (x, y, w, h) in faces:
                            # Extract face region
                            face = frame[y:y+h, x:x+w]

                            # Analyze face for manipulation
                            score = self._analyze_face(face)
                            anomaly_scores.append(score)

                            # Check for visual artifacts
                            artifacts = self._detect_artifacts(face)
                            if artifacts > 0.5:
                                face_inconsistencies.append(frame_idx)

                            # Check compression artifacts (common in deepfakes)
                            compression = self._detect_compression_artifacts(face)
                            compression_artifacts.append(compression)

                    # Temporal consistency check
                    if prev_frame_gray is not None:
                        temporal_diff = self._compute_temporal_consistency(prev_frame_gray, gray)
                        if temporal_diff > 0.6:
                            face_inconsistencies.append(frame_idx)

                    prev_frame_gray = gray.copy()
                    frames_analyzed += 1

                frame_idx += 1

            cap.release()

            # Calculate final scores
            avg_anomaly = np.mean(anomaly_scores) if anomaly_scores else 0.3
            temporal_inconsistency = len(face_inconsistencies) / max(1, frames_analyzed)
            avg_compression = np.mean(compression_artifacts) if compression_artifacts else 0.3

            # Combine scores with weights
            overall_score = (
                avg_anomaly * 0.4 +
                temporal_inconsistency * 0.35 +
                avg_compression * 0.25
            )

            # Determine if deepfake
            is_deepfake = overall_score > 0.55
            confidence = min(0.98, overall_score)

            return {
                "is_deepfake": bool(is_deepfake),
                "confidence": float(confidence),
                "manipulation_type": self._classify_manipulation(avg_anomaly, temporal_inconsistency, avg_compression),
                "details": {
                    "frames_analyzed": frames_analyzed,
                    "anomaly_score": float(avg_anomaly),
                    "temporal_inconsistency": float(temporal_inconsistency),
                    "compression_artifacts": float(avg_compression),
                    "face_inconsistencies": len(face_inconsistencies),
                    "video_duration": f"{frame_count / fps:.2f}s",
                    "fps": int(fps)
                },
                "explanation": self._generate_explanation(is_deepfake, avg_anomaly, temporal_inconsistency, avg_compression)
            }

        except Exception as e:
            return {
                "error": str(e),
                "is_deepfake": False,
                "confidence": 0.0
            }

    def _analyze_face(self, face: np.ndarray) -> float:
        """
        Analyze individual face for deepfake indicators
        Uses edge detection and texture analysis
        """
        try:
            if face.size == 0:
                return 0.3

            gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

            # Analyze texture using Laplacian variance
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            variance = laplacian.var()

            # Check for unnatural smoothness (common in deepfakes)
            smoothness_score = 1.0 - min(1.0, variance / 500.0)

            # Edge analysis
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            edge_score = 1.0 - edge_density if edge_density < 0.15 else edge_density

            # Color analysis for unnatural skin tones
            hsv = cv2.cvtColor(face, cv2.COLOR_BGR2HSV)
            h_channel = hsv[:, :, 0]
            color_variance = np.var(h_channel)
            color_score = min(1.0, abs(color_variance - 20) / 20.0)

            anomaly_score = (smoothness_score * 0.4 + edge_score * 0.3 + color_score * 0.3)
            return min(1.0, anomaly_score)

        except Exception:
            return 0.3

    def _detect_artifacts(self, face: np.ndarray) -> float:
        """
        Detect visual artifacts common in deepfakes
        - Blending artifacts around face boundaries
        - Unnatural texture patterns
        """
        try:
            if face.size == 0:
                return 0.3

            gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

            # Detect high-frequency artifacts
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            variance = laplacian.var()

            # Check for blocking artifacts (JPEG compression from GAN)
            h, w = gray.shape
            if h >= 16 and w >= 16:
                block_score = self._check_blocking_artifacts(gray)
            else:
                block_score = 0.0

            artifact_score = min(1.0, (variance / 1000.0) * 0.6 + block_score * 0.4)
            return artifact_score

        except Exception:
            return 0.3

    def _check_blocking_artifacts(self, gray: np.ndarray) -> float:
        """Check for 8x8 or 16x16 blocking artifacts common in deepfakes"""
        try:
            h, w = gray.shape
            block_differences = []

            for block_size in [8, 16]:
                for i in range(0, h - block_size, block_size):
                    for j in range(0, w - block_size, block_size):
                        # Check edge discontinuities at block boundaries
                        if i + block_size < h and j + block_size < w:
                            # Horizontal boundary
                            top = gray[i + block_size - 1, j:j + block_size]
                            bottom = gray[i + block_size, j:j + block_size]
                            h_diff = np.abs(np.mean(top) - np.mean(bottom))

                            # Vertical boundary
                            left = gray[i:i + block_size, j + block_size - 1]
                            right = gray[i:i + block_size, j + block_size]
                            v_diff = np.abs(np.mean(left) - np.mean(right))

                            block_differences.append((h_diff + v_diff) / 2)

            return min(1.0, np.mean(block_differences) / 10.0) if block_differences else 0.0
        except Exception:
            return 0.0

    def _detect_compression_artifacts(self, face: np.ndarray) -> float:
        """Detect compression artifacts that may indicate manipulation"""
        try:
            if face.size == 0:
                return 0.3

            gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

            # Frequency domain analysis
            dft = cv2.dft(np.float32(gray), flags=cv2.DFT_COMPLEX_OUTPUT)
            dft_shift = np.fft.fftshift(dft)
            magnitude = cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1])

            # High frequency energy (compression creates specific patterns)
            h, w = magnitude.shape
            center_h, center_w = h // 2, w // 2

            # Create high-frequency mask
            y, x = np.ogrid[:h, :w]
            mask = ((x - center_w) ** 2 + (y - center_h) ** 2) > (min(h, w) // 4) ** 2

            high_freq_energy = np.mean(magnitude[mask])
            low_freq_energy = np.mean(magnitude[~mask])

            # Unusual ratio indicates manipulation
            ratio = high_freq_energy / (low_freq_energy + 1e-6)
            compression_score = min(1.0, abs(np.log(ratio + 1e-6)))

            return compression_score

        except Exception:
            return 0.3

    def _compute_temporal_consistency(self, prev_frame: np.ndarray, curr_frame: np.ndarray) -> float:
        """Compute temporal consistency between frames"""
        try:
            # Resize if needed
            if prev_frame.shape != curr_frame.shape:
                curr_frame = cv2.resize(curr_frame, (prev_frame.shape[1], prev_frame.shape[0]))

            # Compute frame difference
            diff = cv2.absdiff(prev_frame, curr_frame)
            mean_diff = np.mean(diff)

            # High differences in successive frames can indicate manipulation
            inconsistency = min(1.0, mean_diff / 50.0)
            return inconsistency
        except Exception:
            return 0.0

    def _classify_manipulation(self, anomaly: float, temporal: float, compression: float) -> str:
        """Classify the type of manipulation detected"""
        if anomaly > 0.7 and temporal > 0.4:
            return "face_swap"
        elif temporal > 0.5:
            return "lip_sync"
        elif anomaly > 0.6:
            return "face_reenactment"
        elif compression > 0.6:
            return "ai_generated"
        else:
            return "none"

    def _generate_explanation(self, is_deepfake: bool, anomaly: float, temporal: float, compression: float) -> str:
        """Generate human-readable explanation of the analysis"""
        if not is_deepfake:
            return "No significant signs of deepfake manipulation detected. The video appears authentic based on facial consistency, temporal analysis, and compression patterns."

        explanations = []
        if anomaly > 0.55:
            explanations.append(f"Facial anomaly score ({anomaly:.2%}) indicates potential manipulation or unusual visual patterns")
        if temporal > 0.3:
            explanations.append(f"Temporal inconsistencies ({temporal:.2%}) detected across video frames suggesting frame-by-frame editing")
        if compression > 0.5:
            explanations.append(f"Compression artifacts ({compression:.2%}) consistent with AI-generated or heavily edited content")

        return " | ".join(explanations) if explanations else "Manipulation indicators detected in video analysis"
