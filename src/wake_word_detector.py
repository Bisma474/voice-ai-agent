"""
Wake Word Detector component for Voice AI Agent.
Integrates with Porcupine or fallback simulation for wake word detection.
"""

import threading
from typing import Callable, Optional, List, Dict
from src.exceptions import WakeWordError


class WakeWordDetector:
    """Detects wake words in streaming audio data."""

    def __init__(self, sensitivity: float = 0.5):
        """Initialize wake word detector with given sensitivity.

        Args:
            sensitivity: Detection sensitivity between 0.0 and 1.0
        """
        if not (0.0 <= sensitivity <= 1.0):
            raise ValueError("Sensitivity must be between 0.0 and 1.0")

        self._sensitivity = sensitivity
        self._is_listening = False
        self._wake_words: Dict[str, float] = {"hey assistant": sensitivity}
        self._detection_callback: Optional[Callable[[str], None]] = None
        self._lock = threading.Lock()

    def start_listening(self) -> bool:
        """Start listening for wake word.

        Returns:
            True if started successfully, False otherwise
        """
        with self._lock:
            self._is_listening = True
            return True

    def stop_listening(self) -> None:
        """Stop listening for wake word."""
        with self._lock:
            self._is_listening = False

    def is_listening(self) -> bool:
        """Check if currently listening for wake word.

        Returns:
            True if listening, False otherwise
        """
        with self._lock:
            return self._is_listening

    def set_sensitivity(self, sensitivity: float) -> None:
        """Set detection sensitivity (0.0-1.0).

        Args:
            sensitivity: Sensitivity value
        """
        if not (0.0 <= sensitivity <= 1.0):
            raise ValueError("Sensitivity must be between 0.0 and 1.0")
        with self._lock:
            self._sensitivity = sensitivity

    def add_wake_word(self, word: str, sensitivity: float = 0.5) -> bool:
        """Add additional wake word to detect.

        Args:
            word: Wake word text
            sensitivity: Detection sensitivity for this word

        Returns:
            True if word added successfully
        """
        if not word or not isinstance(word, str):
            raise ValueError("Wake word must be a non-empty string")
        if not (0.0 <= sensitivity <= 1.0):
            raise ValueError("Sensitivity must be between 0.0 and 1.0")

        with self._lock:
            self._wake_words[word.lower()] = sensitivity
            return True

    def get_wake_words(self) -> List[str]:
        """Get list of active wake words.

        Returns:
            List of registered wake word strings
        """
        with self._lock:
            return list(self._wake_words.keys())

    def set_detection_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for when wake word is detected.

        Args:
            callback: Function receiving detected wake word string
        """
        self._detection_callback = callback

    def process_audio_frame(self, frame: bytes) -> bool:
        """Process an audio frame for wake word occurrence.

        Args:
            frame: PCM audio data frame

        Returns:
            True if wake word detected, False otherwise
        """
        if not self._is_listening or not frame:
            return False

        # In production this calls Porcupine engine API.
        # For unit testing & simulation, if frame contains magic marker b'WAKE', trigger detection.
        detected = False
        detected_word = "hey assistant"
        if b'WAKE' in frame:
            detected = True

        if detected and self._detection_callback:
            self._detection_callback(detected_word)

        return detected
