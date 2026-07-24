"""
Application constants for Voice AI Agent.
"""

from enum import Enum


class SystemState(Enum):
    """System operational states."""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"


class PermissionLevel(Enum):
    """Tool execution permission levels."""
    SAFE = "safe"
    NOTIFY = "notify"
    CONFIRM = "confirm"
    RESTRICTED = "restricted"


# Audio Constants
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_CHANNELS = 1
DEFAULT_CHUNK_SIZE = 1024
DEFAULT_FORMAT = "int16"

# Directory & Path Constants
DEFAULT_APP_DIR = "~/.voice_ai"
DEFAULT_CONFIG_PATH = "~/.voice_ai/config.json"
DEFAULT_TOOLS_DIR = "~/.voice_ai/tools"
DEFAULT_MODELS_DIR = "~/.voice_ai/models"
DEFAULT_LOGS_DIR = "~/.voice_ai/logs"

# Supported STT Model Sizes
STT_MODEL_SIZES = ["tiny", "base", "small", "medium", "large"]

# Supported UI Themes
UI_THEMES = ["light", "dark", "system"]
