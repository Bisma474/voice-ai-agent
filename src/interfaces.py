"""
Abstract interface contracts for Voice AI Agent components.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable


class IConfigManager(ABC):
    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get(self, key_path: str, default: Any = None) -> Any:
        pass

    @abstractmethod
    def set(self, key_path: str, value: Any) -> None:
        pass

    @abstractmethod
    def save_config(self) -> bool:
        pass


class IAudioPipeline(ABC):
    @property
    @abstractmethod
    def is_active(self) -> bool:
        pass

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def set_input_callback(self, callback: Callable[[bytes], None]) -> None:
        pass

    @abstractmethod
    def set_output_callback(self, callback: Callable[[], bytes]) -> None:
        pass


class ISTTEngine(ABC):
    @abstractmethod
    def transcribe(self, audio_data: bytes, sample_rate: int) -> str:
        pass

    @abstractmethod
    def set_language(self, language_code: str) -> None:
        pass

    @abstractmethod
    def unload_model(self) -> None:
        pass


class ILLMEngine(ABC):
    @abstractmethod
    def generate(self, prompt: str, context: Optional[List[Dict[str, Any]]] = None) -> str:
        pass

    @abstractmethod
    def set_parameters(self, **kwargs) -> None:
        pass

    @abstractmethod
    def unload_model(self) -> None:
        pass


class ITTSEngine(ABC):
    @abstractmethod
    def synthesize(self, text: str, voice: Optional[str] = None, speed: float = 1.0) -> bytes:
        pass

    @abstractmethod
    def set_voice(self, voice_name: str) -> None:
        pass


class IWakeWordDetector(ABC):
    @abstractmethod
    def start_listening(self) -> bool:
        pass

    @abstractmethod
    def stop_listening(self) -> None:
        pass

    @abstractmethod
    def set_detection_callback(self, callback: Callable[[str], None]) -> None:
        pass
