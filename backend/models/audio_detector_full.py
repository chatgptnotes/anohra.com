import librosa
import numpy as np
import soundfile as sf
from typing import Dict
import os


class AudioDeepfakeDetector:
    """
    Audio deepfake detection for voice cloning and synthesized speech
    Analyzes spectral and temporal features to detect manipulation
    """

    def __init__(self):
        self.sample_rate = 16000

    async def analyze(self, audio_path: str) -> Dict:
        """
        Comprehensive audio analysis for deepfake/voice cloning detection
        """
        try:
            # Load audio
            audio, sr = librosa.load(audio_path, sr=self.sample_rate)

            # Multiple detection methods
            spectral_analysis = self._spectral_analysis(audio, sr)
            temporal_analysis = self._temporal_analysis(audio)
            voice_consistency = self._voice_consistency_check(audio, sr)
            prosody_analysis = self._prosody_analysis(audio, sr)

            # Combine scores
            overall_score = (
                spectral_analysis * 0.3 +
                temporal_analysis * 0.3 +
                voice_consistency * 0.2 +
                prosody_analysis * 0.2
            )

            is_fake = overall_score > 0.6
            confidence = overall_score

            return {
                "is_deepfake": bool(is_fake),
                "is_voice_cloned": bool(voice_consistency > 0.7),
                "confidence": float(confidence),
                "manipulation_type": self._classify_audio_type(spectral_analysis, voice_consistency),
                "details": {
                    "spectral_anomaly_score": float(spectral_analysis),
                    "temporal_anomaly_score": float(temporal_analysis),
                    "voice_consistency_score": float(voice_consistency),
                    "prosody_score": float(prosody_analysis),
                    "duration": f"{len(audio) / sr:.2f}s",
                    "sample_rate": sr
                },
                "explanation": self._generate_audio_explanation(
                    is_fake, spectral_analysis, temporal_analysis, voice_consistency
                )
            }

        except Exception as e:
            return {
                "error": str(e),
                "is_deepfake": False,
                "confidence": 0.0
            }

    def _spectral_analysis(self, audio: np.ndarray, sr: int) -> float:
        """
        Analyze spectral features for synthetic voice indicators
        - Unnatural harmonic structure
        - Missing frequency components
        - Artificial resonance patterns
        """
        try:
            # Compute spectrogram
            D = librosa.stft(audio)
            S = np.abs(D)

            # Spectral centroid (center of mass of spectrum)
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
            centroid_variance = np.var(spectral_centroids)

            # Spectral rolloff (frequency below which 85% of energy is concentrated)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0]
            rolloff_variance = np.var(spectral_rolloff)

            # Mel-frequency cepstral coefficients (MFCCs)
            mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            mfcc_variance = np.var(mfccs, axis=1).mean()

            # Synthetic voices often have unusual spectral patterns
            # Lower variance indicates more consistent/synthetic characteristics
            consistency_score = 1.0 - min(1.0, centroid_variance / 1000000.0)
            rolloff_score = 1.0 - min(1.0, rolloff_variance / 1000000.0)
            mfcc_score = min(1.0, mfcc_variance / 100.0)

            anomaly_score = (consistency_score * 0.4 + rolloff_score * 0.3 + mfcc_score * 0.3)

            return min(1.0, anomaly_score)

        except Exception:
            return 0.0

    def _temporal_analysis(self, audio: np.ndarray) -> float:
        """
        Analyze temporal patterns for unnatural transitions
        Voice cloning often has abrupt transitions between phonemes
        """
        try:
            # Compute zero-crossing rate
            zcr = librosa.feature.zero_crossing_rate(audio)[0]

            # Analyze transitions (sudden changes indicate synthesis artifacts)
            zcr_diff = np.abs(np.diff(zcr))
            transition_variance = np.var(zcr_diff)

            # Energy envelope
            rms = librosa.feature.rms(y=audio)[0]
            rms_diff = np.abs(np.diff(rms))
            energy_variance = np.var(rms_diff)

            # High variance in transitions can indicate synthetic speech
            transition_score = min(1.0, transition_variance * 1000.0)
            energy_score = min(1.0, energy_variance * 100.0)

            anomaly_score = (transition_score * 0.5 + energy_score * 0.5)

            return min(1.0, anomaly_score)

        except Exception:
            return 0.0

    def _voice_consistency_check(self, audio: np.ndarray, sr: int) -> float:
        """
        Check for voice consistency across the audio
        Real voices have natural variations; cloned voices may be too consistent
        """
        try:
            # Divide audio into segments
            segment_length = sr * 2  # 2-second segments
            num_segments = len(audio) // segment_length

            if num_segments < 2:
                return 0.0

            # Analyze each segment
            segment_features = []
            for i in range(num_segments):
                start = i * segment_length
                end = start + segment_length
                segment = audio[start:end]

                # Extract features
                mfcc = librosa.feature.mfcc(y=segment, sr=sr, n_mfcc=13)
                mfcc_mean = np.mean(mfcc, axis=1)
                segment_features.append(mfcc_mean)

            # Calculate consistency across segments
            segment_features = np.array(segment_features)
            consistency = np.mean([
                np.corrcoef(segment_features[i], segment_features[i+1])[0, 1]
                for i in range(len(segment_features) - 1)
                if not np.isnan(np.corrcoef(segment_features[i], segment_features[i+1])[0, 1])
            ])

            # Very high consistency is suspicious
            if consistency > 0.95:
                return min(1.0, consistency)
            else:
                return max(0.0, (consistency - 0.7) * 2)

        except Exception:
            return 0.0

    def _prosody_analysis(self, audio: np.ndarray, sr: int) -> float:
        """
        Analyze prosody (rhythm, stress, intonation) for naturalness
        Synthetic speech often has unnatural prosody patterns
        """
        try:
            # Extract pitch
            pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)

            # Get pitch track
            pitch_track = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_track.append(pitch)

            if len(pitch_track) < 10:
                return 0.0

            # Analyze pitch variation
            pitch_variance = np.var(pitch_track)
            pitch_range = np.max(pitch_track) - np.min(pitch_track)

            # Natural speech has moderate pitch variation
            # Too little or too much can indicate synthesis
            variance_score = abs(pitch_variance - 5000) / 5000.0
            range_score = abs(pitch_range - 200) / 200.0

            anomaly_score = (variance_score * 0.5 + range_score * 0.5)

            return min(1.0, anomaly_score)

        except Exception:
            return 0.0

    def _classify_audio_type(self, spectral: float, consistency: float) -> str:
        """Classify the type of audio manipulation"""
        if consistency > 0.8:
            return "voice_cloning"
        elif spectral > 0.7:
            return "synthesized_speech"
        elif spectral > 0.5 or consistency > 0.5:
            return "edited"
        else:
            return "authentic"

    def _generate_audio_explanation(self, is_fake: bool, spectral: float, temporal: float, consistency: float) -> str:
        """Generate human-readable explanation"""
        if not is_fake:
            return "Audio appears authentic with natural voice characteristics."

        explanations = []
        if consistency > 0.7:
            explanations.append(f"Abnormally consistent voice patterns ({consistency:.2%}) suggest cloning")
        if spectral > 0.6:
            explanations.append(f"Spectral anomalies ({spectral:.2%}) indicate synthesis")
        if temporal > 0.6:
            explanations.append(f"Unnatural temporal transitions ({temporal:.2%}) detected")

        return " | ".join(explanations) if explanations else "Voice manipulation detected"
