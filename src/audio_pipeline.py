"""
Audio Pipeline Component for Voice AI Agent
Handles audio input/output, buffering, and basic audio processing.
"""

import threading
import queue
import time
from dataclasses import dataclass
from typing import Optional, Callable, Any


@dataclass
class AudioConfig:
    """Audio configuration parameters."""
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    format: str = 'int16'  # In practice, this would map to PyAudio format constants
    input_device_index: Optional[int] = None
    output_device_index: Optional[int] = None


    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.sample_rate <= 0:
            raise ValueError("Sample rate must be positive")
        if self.channels not in [1, 2]:
            raise ValueError("Channels must be 1 (mono) or 2 (stereo)")
        if self.chunk_size <= 0:
            raise ValueError("Chunk size must be positive")
        if self.format not in ['int16', 'int32', 'float32']:
            raise ValueError(f"Unsupported format: {self.format}")


class AudioPipeline:
    """
    Manages audio input and output streams for the voice assistant.

    This class handles:
    - Audio input from microphone
    - Audio output to speakers
    - Basic buffering and flow control
    - Callback registration for audio data processing
    """

    def __init__(self, config: Optional[Any] = None):
        """
        Initialize the audio pipeline.

        Args:
            config: AudioConfig instance or Dictionary containing audio configuration parameters.
                   If None, uses default configuration.
        """
        # Set default configuration
        if isinstance(config, AudioConfig):
            self.config = config
        elif isinstance(config, dict):
            self.config = AudioConfig(**config)
        elif config is None:
            self.config = AudioConfig()
        else:
            self.config = AudioConfig()

        # Internal state
        self._input_stream = None
        self._output_stream = None
        self._is_active = False
        self._input_callback: Optional[Callable[[bytes], None]] = None
        self._output_callback: Optional[Callable[[], bytes]] = None
        self.input_volume: float = 1.0
        self.output_volume: float = 1.0


        # Threading components
        self._input_thread: Optional[threading.Thread] = None
        self._output_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Queues for audio data
        self._input_queue = queue.Queue(maxsize=100)
        self._output_queue = queue.Queue(maxsize=100)

        # Statistics
        self._frames_processed = 0
        self._start_time: Optional[float] = None

    @property
    def is_active(self) -> bool:
        """Check if the audio pipeline is currently active."""
        return self._is_active

    def start(self) -> None:
        """Start the audio input and output streams."""
        if self._is_active:
            return  # Already started

        self._is_active = True
        self._stop_event.clear()
        self._start_time = time.time()

        # In a real implementation, we would initialize PyAudio streams here
        # For this example, we'll simulate the behavior

        # Start input thread (simulated)
        self._input_thread = threading.Thread(target=self._input_loop, daemon=True)
        self._input_thread.start()

        # Start output thread (simulated)
        self._output_thread = threading.Thread(target=self._output_loop, daemon=True)
        self._output_thread.start()

    def stop(self) -> None:
        """Stop the audio input and output streams."""
        if not self._is_active:
            return  # Already stopped

        self._is_active = False
        self._stop_event.set()

        # Wait for threads to finish
        if self._input_thread and self._input_thread.is_alive():
            self._input_thread.join(timeout=2.0)
        if self._output_thread and self._output_thread.is_alive():
            self._output_thread.join(timeout=2.0)

        # Clean up resources
        self._cleanup()

    def set_input_callback(self, callback: Callable[[bytes], None]) -> None:
        """
        Set the callback function for processing incoming audio data.

        Args:
            callback: Function that takes audio data (bytes) and processes it
        """
        self._input_callback = callback

    def set_output_callback(self, callback: Callable[[], bytes]) -> None:
        """
        Set the callback function for getting audio data to play.

        Args:
            callback: Function that returns audio data (bytes) to play
        """
        self._output_callback = callback

    def _input_loop(self) -> None:
        """Simulated input loop for audio data."""
        # In a real implementation, this would read from PyAudio input stream
        # For now, we'll simulate receiving audio data
        while not self._stop_event.is_set():
            # Simulate receiving audio chunk
            time.sleep(0.01)  # Simulate time to collect audio chunk

            # Generate fake audio data (silence)
            audio_chunk = b'\x00\x00' * (self.config.chunk_size // 2)

            # Put in queue for processing
            try:
                self._input_queue.put_nowait(audio_chunk)

                # Call registered callback if available
                if self._input_callback:
                    self._input_callback(audio_chunk)

                self._frames_processed += 1
            except queue.Full:
                # Drop frame if queue is full (in real implementation, might handle differently)
                pass

    def _output_loop(self) -> None:
        """Simulated output loop for audio data."""
        # In a real implementation, this would write to PyAudio output stream
        while not self._stop_event.is_set():
            # Get audio data to play
            try:
                if self._output_callback:
                    audio_data = self._output_callback()
                else:
                    # Generate silence if no callback
                    audio_data = b'\x00\x00' * (self.config.chunk_size // 2)

                # In real implementation, write to output stream
                # For now, just simulate processing
                time.sleep(0.01)

            except Exception as e:
                # Handle errors gracefully
                print(f"Error in output loop: {e}")
                time.sleep(0.1)  # Prevent tight loop on error

    def _cleanup(self) -> None:
        """Clean up audio resources."""
        # In real implementation, close PyAudio streams
        self._input_stream = None
        self._output_stream = None
        self._frames_processed = 0

    def get_statistics(self) -> dict:
        """
        Get processing statistics.

        Returns:
            Dictionary containing processing statistics
        """
        stats = {
            'frames_processed': self._frames_processed,
            'is_active': self._is_active,
        }

        if self._start_time:
            stats['uptime_seconds'] = time.time() - self._start_time
            if stats['uptime_seconds'] > 0:
                stats['fps'] = self._frames_processed / stats['uptime_seconds']

        return stats

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


# Factory function for easy creation
def create_audio_pipeline(config: Optional[dict] = None) -> AudioPipeline:
    """
    Factory function to create an AudioPipeline instance.

    Args:
        config: Optional configuration dictionary

    Returns:
        Configured AudioPipeline instance
    """
    return AudioPipeline(config)