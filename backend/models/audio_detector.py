import numpy as np
from typing import Dict
import wave


class AudioDeepfakeDetector:
    """
    Lightweight audio deepfake detection for voice cloning and synthesized speech
    Note: This is a demonstration version. For production, integrate trained ML models.
    """

    def __init__(self):
        self.sample_rate = 16000

    async def analyze(self, audio_path: str) -> Dict:
        """
        Audio analysis for deepfake/voice cloning detection using signal processing
        """
        try:
            # Read audio file
            audio_data = self._load_audio(audio_path)

            if audio_data is None or len(audio_data) == 0:
                raise Exception("Could not load audio file")

            # Multiple detection methods
            spectral_analysis = self._spectral_analysis(audio_data)
            temporal_analysis = self._temporal_analysis(audio_data)
            voice_consistency = self._voice_consistency_check(audio_data)
            prosody_analysis = self._prosody_analysis(audio_data)

            # Combine scores
            overall_score = (
                spectral_analysis * 0.3 +
                temporal_analysis * 0.3 +
                voice_consistency * 0.2 +
                prosody_analysis * 0.2
            )

            is_fake = overall_score > 0.55
            confidence = min(0.98, overall_score)

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
                    "duration": f"{len(audio_data) / self.sample_rate:.2f}s",
                    "sample_rate": self.sample_rate
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

    def _load_audio(self, audio_path: str):
        """Load audio file and return waveform data"""
        try:
            with wave.open(audio_path, 'rb') as wf:
                sample_rate = wf.getframerate()
                n_frames = wf.getnframes()
                audio_bytes = wf.readframes(n_frames)

                # Convert to numpy array
                if wf.getsampwidth() == 2:  # 16-bit
                    audio_data = np.frombuffer(audio_bytes, dtype=np.int16)
                else:  # 8-bit
                    audio_data = np.frombuffer(audio_bytes, dtype=np.uint8)

                # Normalize
                audio_data = audio_data.astype(np.float32) / np.iinfo(audio_data.dtype).max

                # Resample if needed (simplified - just downsample)
                if sample_rate != self.sample_rate:
                    step = max(1, sample_rate // self.sample_rate)
                    audio_data = audio_data[::step]

                return audio_data
        except Exception as e:
            # Fallback: try to read as raw audio
            try:
                audio_data = np.fromfile(audio_path, dtype=np.float32)
                return audio_data[:self.sample_rate * 60]  # Max 60 seconds
            except:
                return None

    def _spectral_analysis(self, audio: np.ndarray) -> float:
        """
        Analyze spectral features for synthetic voice indicators
        """
        try:
            # Simple FFT-based spectral analysis
            fft = np.fft.fft(audio)
            magnitude = np.abs(fft)[:len(fft)//2]

            # Frequency bins
            freqs = np.fft.fftfreq(len(audio), 1/self.sample_rate)[:len(audio)//2]

            # Analyze spectral centroid (center of mass of spectrum)
            spectral_centroid = np.sum(magnitude * freqs) / (np.sum(magnitude) + 1e-6)

            # Analyze spectral rolloff
            cumsum = np.cumsum(magnitude)
            rolloff_idx = np.where(cumsum >= cumsum[-1] * 0.85)[0]
            spectral_rolloff = freqs[rolloff_idx[0]] if len(rolloff_idx) > 0 else 0

            # Synthetic voices often have unusual spectral characteristics
            # Natural speech typically has centroid around 1000-2000 Hz
            centroid_deviation = abs(spectral_centroid - 1500) / 1500.0

            # Natural speech has rolloff around 3000-5000 Hz
            rolloff_deviation = abs(spectral_rolloff - 4000) / 4000.0

            anomaly_score = min(1.0, (centroid_deviation * 0.5 + rolloff_deviation * 0.5))

            return anomaly_score

        except Exception:
            return 0.3

    def _temporal_analysis(self, audio: np.ndarray) -> float:
        """
        Analyze temporal patterns for unnatural transitions
        """
        try:
            # Compute zero-crossing rate
            zero_crossings = np.sum(np.abs(np.diff(np.sign(audio)))) / (2 * len(audio))

            # Compute energy envelope
            frame_length = self.sample_rate // 100  # 10ms frames
            energy = []
            for i in range(0, len(audio) - frame_length, frame_length):
                frame = audio[i:i+frame_length]
                energy.append(np.sum(frame**2))

            energy = np.array(energy)

            # Analyze transitions (sudden changes indicate synthesis artifacts)
            if len(energy) > 1:
                energy_diff = np.abs(np.diff(energy))
                transition_variance = np.var(energy_diff)

                # Synthetic speech often has more abrupt transitions
                # Normalize the variance
                anomaly_score = min(1.0, transition_variance / (np.mean(energy) + 1e-6))
            else:
                anomaly_score = 0.3

            return anomaly_score

        except Exception:
            return 0.3

    def _voice_consistency_check(self, audio: np.ndarray) -> float:
        """
        Check for voice consistency across the audio
        Real voices have natural variations; cloned voices may be too consistent
        """
        try:
            segment_length = self.sample_rate * 2  # 2-second segments
            num_segments = len(audio) // segment_length

            if num_segments < 2:
                return 0.3

            # Analyze each segment
            segment_features = []
            for i in range(num_segments):
                start = i * segment_length
                end = start + segment_length
                segment = audio[start:end]

                # Extract simple features (mean, std, energy)
                features = [
                    np.mean(segment),
                    np.std(segment),
                    np.mean(segment**2)  # energy
                ]
                segment_features.append(features)

            segment_features = np.array(segment_features)

            # Calculate consistency across segments
            feature_stds = np.std(segment_features, axis=0)
            consistency = 1.0 - np.mean(feature_stds)

            # Very high consistency (low std) is suspicious
            if consistency > 0.95:
                return min(1.0, consistency)
            else:
                return max(0.0, (consistency - 0.7) * 2)

        except Exception:
            return 0.3

    def _prosody_analysis(self, audio: np.ndarray) -> float:
        """
        Analyze prosody (rhythm, stress, intonation) for naturalness
        """
        try:
            # Simple pitch estimation using autocorrelation
            frame_length = self.sample_rate // 50  # 20ms frames
            pitch_track = []

            for i in range(0, len(audio) - frame_length, frame_length):
                frame = audio[i:i+frame_length]

                # Autocorrelation
                autocorr = np.correlate(frame, frame, mode='full')
                autocorr = autocorr[len(autocorr)//2:]

                # Find first peak (fundamental frequency)
                if len(autocorr) > 20:
                    # Skip first few samples
                    peaks = autocorr[20:]
                    if len(peaks) > 0 and np.max(peaks) > 0:
                        peak_idx = np.argmax(peaks) + 20
                        pitch = self.sample_rate / peak_idx if peak_idx > 0 else 0
                        if 50 < pitch < 500:  # Valid pitch range for speech
                            pitch_track.append(pitch)

            if len(pitch_track) < 10:
                return 0.3

            pitch_track = np.array(pitch_track)

            # Analyze pitch variation
            pitch_variance = np.var(pitch_track)
            pitch_range = np.max(pitch_track) - np.min(pitch_track)

            # Natural speech has moderate pitch variation
            # Too little or too much can indicate synthesis
            variance_score = min(1.0, abs(pitch_variance - 300) / 300.0)
            range_score = min(1.0, abs(pitch_range - 150) / 150.0)

            anomaly_score = (variance_score * 0.5 + range_score * 0.5)

            return anomaly_score

        except Exception:
            return 0.3

    def _classify_audio_type(self, spectral: float, consistency: float) -> str:
        """Classify the type of audio manipulation"""
        if consistency > 0.75:
            return "voice_cloning"
        elif spectral > 0.65:
            return "synthesized_speech"
        elif spectral > 0.45 or consistency > 0.45:
            return "edited"
        else:
            return "authentic"

    def _generate_audio_explanation(self, is_fake: bool, spectral: float, temporal: float, consistency: float) -> str:
        """Generate human-readable explanation"""
        if not is_fake:
            return "Audio appears authentic with natural voice characteristics and normal speech patterns."

        explanations = []
        if consistency > 0.65:
            explanations.append(f"Unusually consistent voice patterns ({consistency:.2%}) suggest possible voice cloning or TTS")
        if spectral > 0.55:
            explanations.append(f"Spectral anomalies ({spectral:.2%}) indicate potential synthetic speech generation")
        if temporal > 0.55:
            explanations.append(f"Unnatural temporal transitions ({temporal:.2%}) detected in audio signal")

        return " | ".join(explanations) if explanations else "Voice manipulation or synthesis detected in audio analysis"
