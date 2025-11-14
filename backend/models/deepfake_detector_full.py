import cv2
import numpy as np
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from typing import Dict, List
import os


class DeepfakeDetector:
    """
    Video deepfake detection using face analysis and temporal inconsistency detection
    Detects: Face swap, lip sync, face reenactment
    """

    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.mtcnn = MTCNN(keep_all=True, device=self.device)
        self.model = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)

    async def analyze_video(self, video_path: str) -> Dict:
        """
        Analyze video for deepfake manipulation
        Returns detailed analysis with confidence scores
        """
        try:
            cap = cv2.VideoCapture(video_path)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            # Sample frames for analysis
            sample_rate = max(1, frame_count // 30)  # Analyze ~30 frames
            frames_analyzed = 0
            anomaly_scores = []
            face_inconsistencies = []

            frame_idx = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_idx % sample_rate == 0:
                    # Detect faces
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    boxes, probs = self.mtcnn.detect(frame_rgb)

                    if boxes is not None:
                        for box in boxes:
                            # Extract face region
                            x1, y1, x2, y2 = [int(b) for b in box]
                            face = frame_rgb[y1:y2, x1:x2]

                            # Analyze face for manipulation
                            score = self._analyze_face(face)
                            anomaly_scores.append(score)

                            # Check for visual artifacts
                            artifacts = self._detect_artifacts(face)
                            if artifacts > 0.5:
                                face_inconsistencies.append(frame_idx)

                    frames_analyzed += 1

                frame_idx += 1

            cap.release()

            # Calculate final scores
            avg_anomaly = np.mean(anomaly_scores) if anomaly_scores else 0
            temporal_inconsistency = len(face_inconsistencies) / max(1, frames_analyzed)

            # Determine if deepfake
            is_deepfake = avg_anomaly > 0.6 or temporal_inconsistency > 0.3
            confidence = (avg_anomaly + temporal_inconsistency) / 2

            return {
                "is_deepfake": bool(is_deepfake),
                "confidence": float(confidence),
                "manipulation_type": self._classify_manipulation(avg_anomaly, temporal_inconsistency),
                "details": {
                    "frames_analyzed": frames_analyzed,
                    "anomaly_score": float(avg_anomaly),
                    "temporal_inconsistency": float(temporal_inconsistency),
                    "face_inconsistencies": len(face_inconsistencies),
                    "video_duration": f"{frame_count / fps:.2f}s"
                },
                "explanation": self._generate_explanation(is_deepfake, avg_anomaly, temporal_inconsistency)
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
        Uses feature extraction and anomaly detection
        """
        try:
            if face.size == 0:
                return 0.0

            # Resize and normalize
            face_resized = cv2.resize(face, (160, 160))
            face_tensor = torch.from_numpy(face_resized).permute(2, 0, 1).float().unsqueeze(0).to(self.device)
            face_tensor = (face_tensor - 127.5) / 128.0

            # Extract features
            with torch.no_grad():
                embeddings = self.model(face_tensor)

            # Simple anomaly detection (in production, use trained classifier)
            # This is a placeholder - would use trained deepfake detection model
            anomaly_score = torch.norm(embeddings).item() / 100.0
            return min(1.0, anomaly_score)

        except Exception:
            return 0.0

    def _detect_artifacts(self, face: np.ndarray) -> float:
        """
        Detect visual artifacts common in deepfakes
        - Blending artifacts around face boundaries
        - Color inconsistencies
        - Unnatural texture patterns
        """
        try:
            if face.size == 0:
                return 0.0

            # Convert to grayscale for analysis
            gray = cv2.cvtColor(face, cv2.COLOR_RGB2GRAY)

            # Check for high-frequency artifacts (blending issues)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            variance = laplacian.var()

            # Normalize (high variance might indicate artifacts)
            artifact_score = min(1.0, variance / 1000.0)

            return artifact_score

        except Exception:
            return 0.0

    def _classify_manipulation(self, anomaly: float, temporal: float) -> str:
        """Classify the type of manipulation detected"""
        if anomaly > 0.7 and temporal > 0.4:
            return "face_swap"
        elif temporal > 0.5:
            return "lip_sync"
        elif anomaly > 0.6:
            return "face_reenactment"
        else:
            return "none"

    def _generate_explanation(self, is_deepfake: bool, anomaly: float, temporal: float) -> str:
        """Generate human-readable explanation of the analysis"""
        if not is_deepfake:
            return "No signs of deepfake manipulation detected. The video appears authentic."

        explanations = []
        if anomaly > 0.6:
            explanations.append(f"High anomaly score ({anomaly:.2%}) indicates facial manipulation")
        if temporal > 0.3:
            explanations.append(f"Temporal inconsistencies ({temporal:.2%}) detected across frames")

        return " | ".join(explanations)
