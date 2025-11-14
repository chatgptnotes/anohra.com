import cv2
import numpy as np
from PIL import Image
from typing import Dict


class ImageDeepfakeDetector:
    """
    Lightweight image deepfake detection for:
    - AI-generated images (DALL-E, Stable Diffusion, Midjourney)
    - Face manipulation (swap, morphing)
    - Pixel-level analysis
    Note: This is a demonstration version. For production, integrate trained ML models.
    """

    def __init__(self):
        # Load face detector
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    async def analyze(self, image_path: str) -> Dict:
        """
        Comprehensive image analysis for deepfake/AI-generated content
        """
        try:
            # Load image
            image = Image.open(image_path).convert('RGB')
            image_np = np.array(image)

            # Multiple detection methods
            pixel_analysis = self._pixel_level_analysis(image_np)
            frequency_analysis = self._frequency_domain_analysis(image_np)
            metadata_analysis = self._metadata_analysis(image_path)
            ai_generated_score = self._detect_ai_generated(image_np)
            face_analysis = self._face_manipulation_check(image_np)

            # Combine scores
            overall_score = (
                pixel_analysis * 0.25 +
                frequency_analysis * 0.25 +
                ai_generated_score * 0.30 +
                face_analysis * 0.20
            )

            is_fake = overall_score > 0.60
            confidence = min(0.98, overall_score)

            return {
                "is_deepfake": bool(is_fake),
                "is_ai_generated": bool(ai_generated_score > 0.65),
                "confidence": float(confidence),
                "manipulation_type": self._classify_image_type(pixel_analysis, ai_generated_score, face_analysis),
                "details": {
                    "pixel_analysis_score": float(pixel_analysis),
                    "frequency_analysis_score": float(frequency_analysis),
                    "ai_generated_score": float(ai_generated_score),
                    "face_manipulation_score": float(face_analysis),
                    "metadata_suspicious": metadata_analysis["suspicious"],
                    "image_dimensions": f"{image.width}x{image.height}",
                    "file_format": image.format or "unknown"
                },
                "explanation": self._generate_image_explanation(
                    is_fake, pixel_analysis, frequency_analysis, ai_generated_score, face_analysis
                )
            }

        except Exception as e:
            return {
                "error": str(e),
                "is_deepfake": False,
                "confidence": 0.0
            }

    def _pixel_level_analysis(self, image: np.ndarray) -> float:
        """
        Analyze pixel patterns for manipulation artifacts
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

            # Edge detection
            edges = cv2.Canny(gray, 100, 200)
            edge_density = np.sum(edges > 0) / edges.size

            # Texture analysis
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            variance = laplacian.var()

            # Check for unnatural smoothness (common in AI-generated images)
            smoothness = 1.0 - min(1.0, variance / 1000.0)

            # Color distribution analysis
            color_variance = np.var(image, axis=(0, 1)).mean()
            color_score = min(1.0, abs(color_variance - 500) / 500.0)

            # Combine metrics
            manipulation_score = (smoothness * 0.4 + color_score * 0.3 + (1 - edge_density) * 0.3)

            return min(1.0, manipulation_score)

        except Exception:
            return 0.3

    def _frequency_domain_analysis(self, image: np.ndarray) -> float:
        """
        Analyze frequency domain for GAN/diffusion model artifacts
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

            # Apply FFT
            f_transform = np.fft.fft2(gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude_spectrum = np.abs(f_shift)

            # Analyze high-frequency components
            h, w = magnitude_spectrum.shape
            center_h, center_w = h // 2, w // 2
            radius = min(h, w) // 4

            # Create mask for high frequencies
            y, x = np.ogrid[:h, :w]
            mask = ((x - center_w) ** 2 + (y - center_h) ** 2) > radius ** 2

            high_freq_energy = np.mean(magnitude_spectrum[mask])
            low_freq_energy = np.mean(magnitude_spectrum[~mask])

            # AI-generated images often have unusual frequency ratios
            freq_ratio = high_freq_energy / (low_freq_energy + 1e-6)

            # Normalize
            anomaly_score = min(1.0, abs(np.log(freq_ratio + 1e-6)) / 2.0)

            return anomaly_score

        except Exception:
            return 0.3

    def _metadata_analysis(self, image_path: str) -> Dict:
        """
        Analyze image metadata for manipulation indicators
        """
        try:
            image = Image.open(image_path)
            exif_data = image.getexif() if hasattr(image, 'getexif') else {}

            suspicious = False
            indicators = []

            # Check for missing or suspicious metadata
            if not exif_data or len(exif_data) < 3:
                suspicious = True
                indicators.append("minimal_metadata")

            # Check for AI generation software signatures
            software_tags = [271, 305]  # Make, Software
            for tag in software_tags:
                if tag in exif_data:
                    value = str(exif_data[tag]).lower()
                    if any(ai_tool in value for ai_tool in ['dalle', 'midjourney', 'stable', 'gan', 'diffusion']):
                        suspicious = True
                        indicators.append("ai_software_detected")

            return {
                "suspicious": suspicious,
                "indicators": indicators
            }

        except Exception:
            return {"suspicious": False, "indicators": []}

    def _detect_ai_generated(self, image: np.ndarray) -> float:
        """
        Detect if image is AI-generated
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

            # 1. Unusual noise patterns
            noise = gray.astype(float) - cv2.GaussianBlur(gray, (5, 5), 0).astype(float)
            noise_variance = np.var(noise)
            noise_score = min(1.0, noise_variance / 50.0)

            # 2. Repetitive patterns (common in diffusion models)
            h, w = gray.shape
            block_size = 32
            block_similarities = []

            for i in range(0, min(h - block_size, 200), block_size):
                for j in range(0, min(w - block_size, 200), block_size):
                    block = gray[i:i+block_size, j:j+block_size]
                    if i + block_size * 2 < h:
                        neighbor = gray[i+block_size:i+block_size*2, j:j+block_size]
                        try:
                            correlation = np.corrcoef(block.flatten(), neighbor.flatten())[0, 1]
                            if not np.isnan(correlation):
                                block_similarities.append(abs(correlation))
                        except:
                            pass

            avg_similarity = np.mean(block_similarities) if block_similarities else 0.3

            # 3. Color distribution analysis
            color_variance = np.var(image, axis=(0, 1)).mean()
            color_score = min(1.0, color_variance / 1000.0)

            # 4. JPEG artifact analysis (AI images often have specific compression patterns)
            jpeg_artifacts = self._detect_jpeg_artifacts(gray)

            # Combine indicators
            ai_score = (
                noise_score * 0.25 +
                avg_similarity * 0.30 +
                color_score * 0.25 +
                jpeg_artifacts * 0.20
            )

            return min(1.0, ai_score)

        except Exception:
            return 0.3

    def _detect_jpeg_artifacts(self, gray: np.ndarray) -> float:
        """Detect JPEG compression artifacts"""
        try:
            h, w = gray.shape
            if h < 16 or w < 16:
                return 0.3

            block_discontinuities = []
            for i in range(8, h - 8, 8):
                for j in range(8, w - 8, 8):
                    # Check 8x8 block boundaries
                    top = gray[i-1, j:j+8]
                    bottom = gray[i, j:j+8]
                    left = gray[i:i+8, j-1]
                    right = gray[i:i+8, j]

                    h_disc = np.abs(np.mean(top) - np.mean(bottom))
                    v_disc = np.abs(np.mean(left) - np.mean(right))

                    block_discontinuities.append((h_disc + v_disc) / 2)

            avg_discontinuity = np.mean(block_discontinuities) if block_discontinuities else 0
            return min(1.0, avg_discontinuity / 5.0)

        except Exception:
            return 0.3

    def _face_manipulation_check(self, image: np.ndarray) -> float:
        """Check for face manipulation"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

            if len(faces) == 0:
                return 0.2  # No faces, lower manipulation score

            manipulation_scores = []
            for (x, y, w, h) in faces:
                face = image[y:y+h, x:x+w]

                # Check face boundaries for blending artifacts
                if w > 20 and h > 20:
                    # Sample edges of face
                    top_edge = face[:5, :]
                    bottom_edge = face[-5:, :]
                    left_edge = face[:, :5]
                    right_edge = face[:, -5:]

                    # Calculate variance at edges (manipulation often has smooth edges)
                    edge_variance = np.mean([
                        np.var(top_edge),
                        np.var(bottom_edge),
                        np.var(left_edge),
                        np.var(right_edge)
                    ])

                    # Low variance indicates possible face swap
                    manipulation_score = max(0, 1.0 - edge_variance / 500.0)
                    manipulation_scores.append(manipulation_score)

            return np.mean(manipulation_scores) if manipulation_scores else 0.3

        except Exception:
            return 0.3

    def _classify_image_type(self, pixel_score: float, ai_score: float, face_score: float) -> str:
        """Classify the type of manipulation or generation"""
        if ai_score > 0.7:
            return "ai_generated"
        elif face_score > 0.65:
            return "face_manipulation"
        elif pixel_score > 0.65:
            return "edited"
        else:
            return "authentic"

    def _generate_image_explanation(self, is_fake: bool, pixel: float, freq: float, ai: float, face: float) -> str:
        """Generate human-readable explanation"""
        if not is_fake:
            return "Image appears authentic with no significant manipulation or AI generation detected."

        explanations = []
        if ai > 0.65:
            explanations.append(f"High AI-generation indicators ({ai:.2%}) - likely created by generative model")
        if face > 0.60:
            explanations.append(f"Face manipulation artifacts ({face:.2%}) detected at facial boundaries")
        if pixel > 0.55:
            explanations.append(f"Pixel-level anomalies ({pixel:.2%}) indicate editing or manipulation")
        if freq > 0.55:
            explanations.append(f"Frequency domain signatures ({freq:.2%}) consistent with synthetic content")

        return " | ".join(explanations) if explanations else "Manipulation or AI generation detected"
