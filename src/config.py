"""
Configuration Manager for Voice AI Agent
Handles loading, saving, and accessing application configuration.
"""

import json
import os
from typing import Any, Dict, Optional
from pathlib import Path


class ConfigManager:
    """Manages application configuration with persistent storage."""

    # Default configuration values
    DEFAULT_CONFIG = {
        "audio": {
            "sample_rate": 16000,
            "channels": 1,
            "chunk_size": 1024,
            "format": "int16",
            "input_device_index": None,
            "output_device_index": None
        },
        "stt": {
            "model_path": None,  # Will be set based on model selection
            "language": "en",
            "model_size": "base",  # tiny, base, small, medium, large
            "use_gpu": False
        },
        "llm": {
            "model_path": None,  # Will be set based on model selection
            "context_length": 2048,
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 512,
            "repeat_penalty": 1.1,
            "use_gpu": False
        },
        "tts": {
            "model_path": None,  # Will be set based on model selection
            "use_fallback": True,
            "voice": "default",
            "speed": 1.0,
            "volume": 0.8
        },
        "wake_word": {
            "sensitivity": 0.5,
            "wake_words": ["hey assistant"],
            "access_key": None  # For Porcupine
        },
        "tools": {
            "enabled": True,
            "tools_directory": "~/.voice_ai/tools",
            "permission_level": "notify"  # safe, notify, confirm, restricted
        },
        "ui": {
            "theme": "system",  # light, dark, system
            "show_system_tray": True,
            "animate_ui": True,
            "font_size": 10
        },
        "api_keys": {
            "groq_api_key": None,
            "openai_api_key": None,
            "gemini_api_key": None,
            "elevenlabs_api_key": None
        },
        "providers": {
            "llm": "groq",        # groq, openai, gemini, local
            "stt": "whisper",     # whisper, groq, deepgram, local
            "tts": "elevenlabs"   # elevenlabs, gtts, local
        },
        "privacy": {
            "save_history": False,
            "history_length": 50,
            "data_retention_days": 30,
            "allow_telemetry": False
        }
    }


    _instance = None
    _initialized_paths = set()  # Track which paths have been initialized

    def __new__(cls, config_path: str = None):
        """Implement singleton pattern for global access per config path."""
        if config_path is None:
            config_path = str(Path.home() / ".voice_ai" / "config.json")

        if config_path not in cls._initialized_paths:
            instance = super(ConfigManager, cls).__new__(cls)
            instance._initialized = False
            instance._config_path = Path(config_path)
            cls._instance = instance
            cls._initialized_paths.add(config_path)
        return cls._instance

    def __init__(self, config_path: str = None):
        """Initialize configuration manager with optional custom config path.

        Args:
            config_path: Path to configuration file. If None, uses default location.
        """
        # Handle default path
        if config_path is None:
            config_path = str(Path.home() / ".voice_ai" / "config.json")

        # Prevent re-initialization of singleton for same path
        if hasattr(self, '_initialized') and self._initialized and str(self._config_path) == config_path:
            return

        # Set config path
        self._config_path = Path(config_path)

        # Create directory if it doesn't exist
        self._config_path.parent.mkdir(parents=True, exist_ok=True)

        # Load or create configuration
        self._config = self._load_or_create_default()
        self._initialized = True

    def _load_or_create_default(self) -> Dict[str, Any]:
        """Load configuration from file or create default if file doesn't exist."""
        import copy
        try:
            if self._config_path.exists():
                with open(self._config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return self._deep_merge(copy.deepcopy(self.DEFAULT_CONFIG), loaded_config)
            else:
                # No config file exists, create default
                return copy.deepcopy(self.DEFAULT_CONFIG)
        except Exception as e:
            # If there's an error loading, return default and log warning
            print(f"Warning: Could not load config from {self._config_path}: {e}")
            print("Using default configuration.")
            return copy.deepcopy(self.DEFAULT_CONFIG)


    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge two dictionaries.

        Args:
            base: Base dictionary to merge into
            update: Dictionary with updates to apply

        Returns:
            Merged dictionary
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
        return base

    def get_config(self) -> Dict[str, Any]:
        """Return complete configuration dictionary.

        Returns:
            Copy of the current configuration dictionary
        """
        return self._config.copy()

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation.

        Args:
            key_path: Dot-separated path to configuration value (e.g., 'audio.sample_rate')
            default: Default value to return if key_path is not found

        Returns:
            Configuration value at key_path or default if not found
        """
        keys = key_path.split('.')
        value = self._config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value using dot notation.

        Args:
            key_path: Dot-separated path to configuration value (e.g., 'audio.sample_rate')
            value: Value to set at the specified path
        """
        keys = key_path.split('.')
        target = self._config

        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]

        # Set the value at the target location
        target[keys[-1]] = value

    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values.

        Args:
            updates: Dictionary containing updates to apply to configuration
        """
        self._deep_merge(self._config, updates)

    def validate_config(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Validate configuration values against expected types and ranges.

        Args:
            config: Configuration dictionary to validate. If None, validates current config.

        Returns:
            True if valid, raises ValueError if invalid.
        """
        cfg = config if config is not None else self._config
        
        # Audio validation
        audio = cfg.get('audio', {})
        if 'sample_rate' in audio and (not isinstance(audio['sample_rate'], int) or audio['sample_rate'] <= 0):
            raise ValueError("sample_rate must be a positive integer")
        if 'channels' in audio and (not isinstance(audio['channels'], int) or audio['channels'] not in (1, 2)):
            raise ValueError("channels must be 1 or 2")
        if 'chunk_size' in audio and (not isinstance(audio['chunk_size'], int) or audio['chunk_size'] <= 0):
            raise ValueError("chunk_size must be a positive integer")

        # STT validation
        stt = cfg.get('stt', {})
        valid_model_sizes = ["tiny", "base", "small", "medium", "large"]
        if 'model_size' in stt and stt['model_size'] not in valid_model_sizes:
            raise ValueError(f"model_size must be one of {valid_model_sizes}")

        # TTS validation
        tts = cfg.get('tts', {})
        if 'speed' in tts and (not isinstance(tts['speed'], (int, float)) or not (0.5 <= tts['speed'] <= 2.0)):
            raise ValueError("speed must be between 0.5 and 2.0")
        if 'volume' in tts and (not isinstance(tts['volume'], (int, float)) or not (0.0 <= tts['volume'] <= 1.0)):
            raise ValueError("volume must be between 0.0 and 1.0")

        # Wake word validation
        wake = cfg.get('wake_word', {})
        if 'sensitivity' in wake and (not isinstance(wake['sensitivity'], (int, float)) or not (0.0 <= wake['sensitivity'] <= 1.0)):
            raise ValueError("sensitivity must be between 0.0 and 1.0")

        # Tools validation
        tools = cfg.get('tools', {})
        valid_permissions = ["safe", "notify", "confirm", "restricted"]
        if 'permission_level' in tools and tools['permission_level'] not in valid_permissions:
            raise ValueError(f"permission_level must be one of {valid_permissions}")

        # UI validation
        ui = cfg.get('ui', {})
        valid_themes = ["light", "dark", "system"]
        if 'theme' in ui and ui['theme'] not in valid_themes:
            raise ValueError(f"theme must be one of {valid_themes}")

        return True

    def save_config(self) -> bool:
        """Save current configuration to persistent storage.

        Returns:
            True if save was successful, False otherwise
        """
        try:
            self.validate_config()
            # Ensure directory exists
            self._config_path.parent.mkdir(parents=True, exist_ok=True)

            # Write configuration to file
            with open(self._config_path, 'w') as f:
                json.dump(self._config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config to {self._config_path}: {e}")
            return False

    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        import copy
        self._config = copy.deepcopy(self.DEFAULT_CONFIG)
        self.save_config()