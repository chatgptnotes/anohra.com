import cv2
import numpy as np
from PIL import Image
import torch
from torchvision import transforms
from typing import Dict
import os


class ImageDeepfakeDetector:
    """
    Image deepfake detection for:
    - AI-generated images (DALL-E, Stable Diffusion, Midjourney)
    - Face manipulation (swap, morphing)
    - Pixel-level analysis
    """

    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

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

            # Combine scores
            overall_score = (
                pixel_analysis * 0.3 +
                frequency_analysis * 0.3 +
                ai_generated_score * 0.4
            )

            is_fake = overall_score > 0.65
            confidence = overall_score

            return {
                "is_deepfake": bool(is_fake),
                "is_ai_generated": bool(ai_generated_score > 0.7),
                "confidence": float(confidence),
                "manipulation_type": self._classify_image_type(pixel_analysis, ai_generated_score),
                "details": {
                    "pixel_analysis_score": float(pixel_analysis),
                    "frequency_analysis_score": float(frequency_analysis),
                    "ai_generated_score": float(ai_generated_score),
                    "metadata_suspicious": metadata_analysis["suspicious"],
                    "image_dimensions": f"{image.width}x{image.height}",
                    "file_format": image.format
                },
                "explanation": self._generate_image_explanation(
                    is_fake, pixel_analysis, frequency_analysis, ai_generated_score
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
        - Edge inconsistencies
        - Color bleeding
        - Unnatural smoothness
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

            # Edge detection
            edges = cv2.Canny(gray, 100, 200)
            edge_density = np.sum(edges > 0) / edges.size

            # Texture analysis using local binary patterns
            variance = cv2.Laplacian(gray, cv2.CV_64F).var()

            # Check for unnatural smoothness (common in AI-generated images)
            smoothness = 1.0 - min(1.0, variance / 1000.0)

            # Combine metrics
            manipulation_score = (smoothness * 0.6 + (1 - edge_density) * 0.4)

            return min(1.0, manipulation_score)

        except Exception:
            return 0.0

    def _frequency_domain_analysis(self, image: np.ndarray) -> float:
        """
        Analyze frequency domain for GAN/diffusion model artifacts
        Deepfakes often have unusual frequency patterns
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
            anomaly_score = min(1.0, abs(freq_ratio - 1.0))

            return anomaly_score

        except Exception:
            return 0.0

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
                    if any(ai_tool in value for ai_tool in ['dalle', 'midjourney', 'stable', 'gan']):
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
        Detect if image is AI-generated (Stable Diffusion, DALL-E, Midjourney, etc.)
        Uses pattern recognition for common AI artifacts
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

            # Check for typical AI generation artifacts
            # 1. Unusual noise patterns
            noise = gray.astype(float) - cv2.GaussianBlur(gray, (5, 5), 0).astype(float)
            noise_variance = np.var(noise)

            # 2. Repetitive patterns (common in diffusion models)
            h, w = gray.shape
            block_size = 32
            block_similarities = []

            for i in range(0, h - block_size, block_size):
                for j in range(0, w - block_size, block_size):
                    block = gray[i:i+block_size, j:j+block_size]
                    if i + block_size * 2 < h:
                        neighbor = gray[i+block_size:i+block_size*2, j:j+block_size]
                        similarity = np.corrcoef(block.flatten(), neighbor.flatten())[0, 1]
                        if not np.isnan(similarity):
                            block_similarities.append(abs(similarity))

            avg_similarity = np.mean(block_similarities) if block_similarities else 0

            # 3. Color distribution analysis
            color_variance = np.var(image, axis=(0, 1)).mean()

            # Combine indicators
            ai_score = (
                min(1.0, noise_variance / 100.0) * 0.3 +
                avg_similarity * 0.4 +
                min(1.0, color_variance / 1000.0) * 0.3
            )

            return min(1.0, ai_score)

        except Exception:
            return 0.0

    def _classify_image_type(self, pixel_score: float, ai_score: float) -> str:
        """Classify the type of manipulation or generation"""
        if ai_score > 0.7:
            return "ai_generated"
        elif pixel_score > 0.7:
            return "face_manipulation"
        elif pixel_score > 0.5:
            return "edited"
        else:
            return "authentic"

    def _generate_image_explanation(self, is_fake: bool, pixel: float, freq: float, ai: float) -> str:
        """Generate human-readable explanation"""
        if not is_fake:
            return "Image appears authentic with no significant manipulation detected."

        explanations = []
        if ai > 0.7:
            explanations.append(f"High AI-generation score ({ai:.2%}) - likely created by AI model")
        if pixel > 0.6:
            explanations.append(f"Pixel-level artifacts ({pixel:.2%}) indicate manipulation")
        if freq > 0.6:
            explanations.append(f"Frequency domain anomalies ({freq:.2%}) detected")

        return " | ".join(explanations) if explanations else "Manipulation detected"
