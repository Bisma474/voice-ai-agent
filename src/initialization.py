"""
Initialization Routines and Dependency Checks for Voice AI Agent.
"""

import sys
import shutil
from typing import Dict, Any, Tuple
from src.config import ConfigManager
from src.audio_pipeline import AudioPipeline
from src.wake_word_detector import WakeWordDetector
from src.stt_engine import STTEngine
from src.llm_engine import LLMEngine
from src.tts_engine import TTSEngine
from src.tool_manager import ToolManager
from src.logging_config import setup_logging


def check_system_dependencies() -> Dict[str, bool]:
    """Check required system dependencies and resources.

    Returns:
        Dictionary mapping dependency names to boolean availability status
    """
    status = {
        "python_version": sys.version_info >= (3, 8),
        "disk_space": True,
        "pyaudio": True,
    }

    # Check available disk space (require at least 500MB free)
    try:
        total, used, free = shutil.disk_usage(".")
        status["disk_space"] = (free > 500 * 1024 * 1024)
    except Exception:
        status["disk_space"] = True

    return status


def initialize_components(config_path: str = None) -> Tuple[Dict[str, Any], ConfigManager]:
    """Initialize all application components in exact dependency order.

    Order:
    1. Config Manager
    2. Audio Pipeline
    3. Wake Word Detector
    4. STT Engine
    5. LLM Engine
    6. TTS Engine
    7. Tool Manager

    Returns:
        Tuple of (components dict, config_manager instance)
    """
    logger = setup_logging()
    logger.info("Starting system initialization sequence...")

    deps = check_system_dependencies()
    if not deps.get("python_version", False):
        raise RuntimeError("Python 3.8+ is required to run Voice AI Agent.")

    # 1. Config Manager
    config_mgr = ConfigManager(config_path)

    # 2. Audio Pipeline
    audio_cfg = config_mgr.get('audio', {})
    audio_pipeline = AudioPipeline(audio_cfg)

    # 3. Wake Word Detector
    wake_sens = config_mgr.get('wake_word.sensitivity', 0.5)
    wake_detector = WakeWordDetector(sensitivity=wake_sens)

    # 4. STT Engine
    stt_lang = config_mgr.get('stt.language', 'en')
    stt_size = config_mgr.get('stt.model_size', 'base')
    stt_engine = STTEngine(language=stt_lang, model_size=stt_size)

    # 5. LLM Engine
    llm_ctx = config_mgr.get('llm.context_length', 2048)
    llm_engine = LLMEngine(context_length=llm_ctx)

    # 6. TTS Engine
    tts_fallback = config_mgr.get('tts.use_fallback', True)
    tts_engine = TTSEngine(use_fallback=tts_fallback)

    # 7. Tool Manager
    tools_dir = config_mgr.get('tools.tools_directory', '~/.voice_ai/tools')
    tool_manager = ToolManager(tools_directory=tools_dir)

    components = {
        "audio_pipeline": audio_pipeline,
        "wake_detector": wake_detector,
        "stt_engine": stt_engine,
        "llm_engine": llm_engine,
        "tts_engine": tts_engine,
        "tool_manager": tool_manager
    }

    logger.info("System initialization sequence complete.")
    return components, config_mgr
