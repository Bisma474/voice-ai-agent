"""
Main Application Entry Point and Orchestrator for Voice AI Agent.
Coordinates all pipeline components, state transitions, and event flow.
"""

import sys
import time
import threading
from typing import Optional, Dict, Any

from src.constants import SystemState
from src.config import ConfigManager
from src.audio_pipeline import AudioPipeline
from src.wake_word_detector import WakeWordDetector
from src.stt_engine import STTEngine
from src.llm_engine import LLMEngine
from src.tts_engine import TTSEngine
from src.tool_manager import ToolManager
from src.event_system import EventBus, EventType
from src.logging_config import setup_logging
from src.exceptions import VoiceAIAgentError


class VoiceAIAgent:
    """Main application orchestrator for Voice AI Agent."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize agent and load all components.

        Args:
            config_path: Path to configuration file
        """
        self.logger = setup_logging()
        self.logger.info("Initializing Voice AI Agent...")

        self.config_manager = ConfigManager(config_path)
        self.event_bus = EventBus()
        self.state = SystemState.IDLE

        # Initialize core components
        audio_cfg = self.config_manager.get('audio', {})
        self.audio_pipeline = AudioPipeline(audio_cfg)

        wake_sens = self.config_manager.get('wake_word.sensitivity', 0.5)
        self.wake_word_detector = WakeWordDetector(sensitivity=wake_sens)

        stt_lang = self.config_manager.get('stt.language', 'en')
        stt_size = self.config_manager.get('stt.model_size', 'base')
        self.stt_engine = STTEngine(language=stt_lang, model_size=stt_size)

        llm_ctx = self.config_manager.get('llm.context_length', 2048)
        self.llm_engine = LLMEngine(context_length=llm_ctx)

        tts_fallback = self.config_manager.get('tts.use_fallback', True)
        self.tts_engine = TTSEngine(use_fallback=tts_fallback)

        tools_dir = self.config_manager.get('tools.tools_directory', '~/.voice_ai/tools')
        self.tool_manager = ToolManager(tools_directory=tools_dir)

        # Connect internal callbacks
        self.wake_word_detector.set_detection_callback(self._on_wake_word_detected)
        self.audio_pipeline.set_input_callback(self._on_audio_data_received)

        self._running = False
        self._lock = threading.Lock()

    def set_state(self, new_state: SystemState) -> None:
        """Transition system state and publish event.

        Args:
            new_state: SystemState target enum
        """
        with self._lock:
            old_state = self.state
            self.state = new_state
            self.logger.info(f"State transition: {old_state.value} -> {new_state.value}")
            self.event_bus.publish(EventType.STATE_CHANGED, {
                "old_state": old_state,
                "new_state": new_state
            })

    def start(self) -> None:
        """Start the voice AI agent service."""
        self.logger.info("Starting Voice AI Agent service...")
        self._running = True

        self.audio_pipeline.start()
        self.wake_word_detector.start_listening()
        self.set_state(SystemState.IDLE)

    def stop(self) -> None:
        """Stop the voice AI agent service and cleanup resources."""
        self.logger.info("Stopping Voice AI Agent service...")
        self._running = False

        self.wake_word_detector.stop_listening()
        self.audio_pipeline.stop()
        self.set_state(SystemState.IDLE)

    def process_voice_turn(self, audio_data: bytes) -> str:
        """Execute a full processing pipeline turn: STT -> LLM/Tool -> TTS.

        Args:
            audio_data: Raw PCM audio input bytes

        Returns:
            Generated response string
        """
        try:
            self.set_state(SystemState.PROCESSING)

            # 1. Speech to Text
            transcription = self.stt_engine.transcribe(audio_data)
            self.event_bus.publish(EventType.TRANSCRIPTION_COMPLETE, transcription)

            if not transcription:
                self.logger.info("No speech recognized in turn.")
                self.set_state(SystemState.IDLE)
                return ""

            # 2. LLM Engine / Tool match
            llm_response = self.llm_engine.generate(transcription)

            # Check if LLM output triggered a tool call
            if llm_response.startswith("[TOOL_CALL:") and llm_response.endswith("]"):
                tool_name = llm_response[11:-1]
                tool_result = self.tool_manager.execute_tool(tool_name, {})
                if tool_result.success:
                    response_text = f"Tool {tool_name} returned: {tool_result.result}"
                else:
                    response_text = f"Tool {tool_name} failed: {tool_result.error}"
            else:
                response_text = llm_response

            self.event_bus.publish(EventType.RESPONSE_GENERATED, response_text)

            # 3. Text to Speech
            self.set_state(SystemState.SPEAKING)
            tts_audio = self.tts_engine.synthesize(response_text)
            self.event_bus.publish(EventType.SYNTHESIS_COMPLETE, len(tts_audio))

            self.set_state(SystemState.IDLE)
            return response_text

        except Exception as e:
            self.logger.error(f"Error during voice turn processing: {e}")
            self.set_state(SystemState.ERROR)
            self.event_bus.publish(EventType.ERROR_OCCURRED, str(e))
            return f"An error occurred: {e}"

    def _on_wake_word_detected(self, wake_word: str) -> None:
        """Internal handler when wake word is detected."""
        self.logger.info(f"Wake word detected: {wake_word}")
        self.event_bus.publish(EventType.WAKE_WORD_DETECTED, wake_word)
        self.set_state(SystemState.LISTENING)

    def _on_audio_data_received(self, data: bytes) -> None:
        """Internal audio streaming callback."""
        if self.wake_word_detector.is_listening():
            self.wake_word_detector.process_audio_frame(data)


def main():
    """CLI entry point."""
    agent = VoiceAIAgent()
    agent.start()
    print("Voice AI Agent running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nShutting down...")
        agent.stop()


if __name__ == '__main__':
    main()
