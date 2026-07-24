"""
Text-to-Speech Engine component for Voice AI Agent.
Integrates with gTTS (Google Text-to-Speech) for free, unlimited audio synthesis.
Falls back to PCM simulation for offline/test use.
"""

from typing import List, Dict, Any, Optional
from src.exceptions import TTSEngineError
from src.utils import chunk_text, normalize_text


class TTSEngine:
    """Manages text synthesis into audio using gTTS (Google TTS) or PCM fallback."""

    AVAILABLE_VOICES = ["default", "female", "male", "neutral"]

    def __init__(self, model_path: Optional[str] = None, use_fallback: bool = True):
        """Initialize TTS engine.

        Args:
            model_path: Path to TTS model file (unused for gTTS)
            use_fallback: Whether to use PCM silence fallback if gTTS fails
        """
        self._model_path = model_path
        self._use_fallback = use_fallback
        self._current_voice = "default"
        self._rate = 1.0
        self._volume = 0.8
        self._language = "en"   # gTTS language code

    def synthesize(self, text: str, voice: Optional[str] = None, speed: float = 1.0) -> bytes:
        """Synthesize text into audio bytes using gTTS.

        Args:
            text: Text to synthesize
            voice: Optional voice identifier
            speed: Speech rate multiplier (0.5-2.0)

        Returns:
            MP3 audio bytes from gTTS, or raw PCM bytes as fallback
        """
        cleaned_text = normalize_text(text)
        if not cleaned_text:
            return b""

        if not (0.5 <= speed <= 2.0):
            raise ValueError("Speech speed must be between 0.5 and 2.0")

        # --- Primary: gTTS (Google Text-to-Speech, free & unlimited) ---
        try:
            from gtts import gTTS
            import io
            tts = gTTS(text=cleaned_text, lang=self._language, slow=(speed < 0.8))
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            return audio_buffer.read()
        except ImportError:
            pass  # gTTS not installed, fall through to PCM fallback
        except Exception as e:
            print(f"gTTS error: {e} — using PCM fallback")

        # --- Fallback: PCM silence (for offline/test use) ---
        chunks = chunk_text(cleaned_text, max_chars=300)
        total_audio = bytearray()
        for chunk in chunks:
            # 16000 Hz, 16-bit mono = 32000 bytes per second of speech
            # Approximate speech rate ~ 15 characters per second
            sec = max(0.5, (len(chunk) / 15.0) / speed)
            num_bytes = int(sec * 32000)
            if num_bytes % 2 != 0:
                num_bytes += 1
            total_audio.extend(b'\x00\x00' * (num_bytes // 2))

        return bytes(total_audio)

    def set_voice(self, voice_name: str) -> None:
        """Set voice for synthesis.

        Args:
            voice_name: Voice identifier
        """
        if voice_name not in self.AVAILABLE_VOICES:
            raise ValueError(f"Unknown voice '{voice_name}'. Available: {self.AVAILABLE_VOICES}")
        self._current_voice = voice_name

    def set_language(self, lang: str) -> None:
        """Set gTTS language code (e.g. 'en', 'fr', 'ur', 'ar').

        Args:
            lang: BCP-47 language code supported by gTTS
        """
        self._language = lang

    def set_rate(self, rate: float) -> None:
        """Set speech rate (0.5-2.0).

        Args:
            rate: Speech speed multiplier
        """
        if not (0.5 <= rate <= 2.0):
            raise ValueError("Speech rate must be between 0.5 and 2.0")
        self._rate = rate

    def get_available_voices(self) -> List[str]:
        """Get list of available voices.

        Returns:
            List of voice names
        """
        return self.AVAILABLE_VOICES.copy()

    def get_voice_info(self, voice_name: str) -> Dict[str, Any]:
        """Get information about specific voice.

        Args:
            voice_name: Voice identifier

        Returns:
            Dictionary containing voice metadata
        """
        if voice_name not in self.AVAILABLE_VOICES:
            raise ValueError(f"Unknown voice '{voice_name}'")
        return {
            "name": voice_name,
            "language": self._language,
            "gender": voice_name if voice_name in ["female", "male"] else "neutral",
            "is_default": voice_name == self._current_voice,
            "provider": "gTTS"
        }
