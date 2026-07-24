"""
Custom exception classes for Voice AI Agent.
"""


class VoiceAIAgentError(Exception):
    """Base exception for Voice AI Agent errors."""
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"


class ConfigError(VoiceAIAgentError):
    """Raised when configuration operation fails."""
    def __init__(self, message: str):
        super().__init__(message, error_code="CONFIG_ERROR")


class AudioPipelineError(VoiceAIAgentError):
    """Raised when audio input/output operation fails."""
    def __init__(self, message: str):
        super().__init__(message, error_code="AUDIO_ERROR")


class STTEngineError(VoiceAIAgentError):
    """Raised when speech-to-text processing fails."""
    def __init__(self, message: str):
        super().__init__(message, error_code="STT_ERROR")


class LLMEngineError(VoiceAIAgentError):
    """Raised when language model processing fails."""
    def __init__(self, message: str):
        super().__init__(message, error_code="LLM_ERROR")


class TTSEngineError(VoiceAIAgentError):
    """Raised when text-to-speech synthesis fails."""
    def __init__(self, message: str):
        super().__init__(message, error_code="TTS_ERROR")


class WakeWordError(VoiceAIAgentError):
    """Raised when wake word detector operation fails."""
    def __init__(self, message: str):
        super().__init__(message, error_code="WAKE_WORD_ERROR")


class ToolError(VoiceAIAgentError):
    """Raised when tool execution or management fails."""
    def __init__(self, message: str):
        super().__init__(message, error_code="TOOL_ERROR")


class ToolPermissionError(ToolError):
    """Raised when tool execution permission is denied."""
    def __init__(self, message: str):
        super().__init__(message)
        self.error_code = "TOOL_PERMISSION_ERROR"


class UIManagerError(VoiceAIAgentError):
    """Raised when UI operation fails."""
    def __init__(self, message: str):
        super().__init__(message, error_code="UI_ERROR")
