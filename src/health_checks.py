"""
Health Checks and Diagnostics for Voice AI Agent.
"""

from typing import Dict, Any


def run_health_checks(components: Dict[str, Any]) -> Dict[str, Any]:
    """Run diagnostic health checks on all loaded components.

    Args:
        components: Dictionary of component instances

    Returns:
        Health report dictionary containing status of each component
    """
    report = {
        "status": "healthy",
        "components": {}
    }

    overall_healthy = True

    # Audio pipeline check
    audio_pipeline = components.get("audio_pipeline")
    if audio_pipeline:
        report["components"]["audio_pipeline"] = {
            "status": "ok",
            "is_active": audio_pipeline.is_active,
            "stats": audio_pipeline.get_statistics()
        }
    else:
        report["components"]["audio_pipeline"] = {"status": "error", "message": "Missing component"}
        overall_healthy = False

    # Wake word detector check
    wake_detector = components.get("wake_detector")
    if wake_detector:
        report["components"]["wake_detector"] = {
            "status": "ok",
            "is_listening": wake_detector.is_listening(),
            "wake_words": wake_detector.get_wake_words()
        }
    else:
        report["components"]["wake_detector"] = {"status": "error", "message": "Missing component"}
        overall_healthy = False

    # STT engine check
    stt_engine = components.get("stt_engine")
    if stt_engine:
        report["components"]["stt_engine"] = {
            "status": "ok",
            "info": stt_engine.get_model_info()
        }
    else:
        report["components"]["stt_engine"] = {"status": "error", "message": "Missing component"}
        overall_healthy = False

    # LLM engine check
    llm_engine = components.get("llm_engine")
    if llm_engine:
        report["components"]["llm_engine"] = {
            "status": "ok",
            "token_test": llm_engine.get_token_count("Health check test phrase") > 0
        }
    else:
        report["components"]["llm_engine"] = {"status": "error", "message": "Missing component"}
        overall_healthy = False

    # TTS engine check
    tts_engine = components.get("tts_engine")
    if tts_engine:
        report["components"]["tts_engine"] = {
            "status": "ok",
            "voices": len(tts_engine.get_available_voices())
        }
    else:
        report["components"]["tts_engine"] = {"status": "error", "message": "Missing component"}
        overall_healthy = False

    # Tool manager check
    tool_manager = components.get("tool_manager")
    if tool_manager:
        report["components"]["tool_manager"] = {
            "status": "ok",
            "tools_count": len(tool_manager.list_available_tools())
        }
    else:
        report["components"]["tool_manager"] = {"status": "error", "message": "Missing component"}
        overall_healthy = False

    report["status"] = "healthy" if overall_healthy else "unhealthy"
    return report
