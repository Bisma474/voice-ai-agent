"""
Logging configuration for Voice AI Agent.
"""

import logging
import os
from pathlib import Path
from typing import Optional


def setup_logging(log_dir: Optional[str] = None, level: str = "INFO") -> logging.Logger:
    """Configure application logging.

    Args:
        log_dir: Directory to save log files. Defaults to ~/.voice_ai/logs
        level: Logging level string ('DEBUG', 'INFO', 'WARNING', 'ERROR')

    Returns:
        Configured root logger instance.
    """
    if log_dir is None:
        log_dir = str(Path.home() / ".voice_ai" / "logs")

    log_path = Path(os.path.expanduser(log_dir))
    log_path.mkdir(parents=True, exist_ok=True)

    log_file = log_path / "voice_ai_agent.log"

    log_level = getattr(logging, level.upper(), logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger("voice_ai_agent")
    logger.setLevel(log_level)

    # Clear existing handlers to allow reconfiguration (e.g. during testing)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler(str(log_file), encoding='utf-8')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


    return logger
