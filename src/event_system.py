"""
Event System / Event Bus component for Voice AI Agent.
Enables loosely-coupled event-driven communication between components.
"""

import threading
from enum import Enum
from typing import Callable, Dict, List, Any


class EventType(Enum):
    """Supported event types in the Voice AI system."""
    WAKE_WORD_DETECTED = "wake_word_detected"
    SPEECH_STARTED = "speech_started"
    SPEECH_ENDED = "speech_ended"
    TRANSCRIPTION_COMPLETE = "transcription_complete"
    RESPONSE_GENERATED = "response_generated"
    SYNTHESIS_COMPLETE = "synthesis_complete"
    STATE_CHANGED = "state_changed"
    ERROR_OCCURRED = "error_occurred"


class Event:
    """Represents an event notification."""

    def __init__(self, event_type: EventType, data: Any = None):
        self.type = event_type
        self.data = data


class EventBus:
    """Thread-safe event bus for publishing and subscribing to system events."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EventBus, cls).__new__(cls)
                cls._instance._subscribers: Dict[EventType, List[Callable[[Event], None]]] = {}
                cls._instance._sub_lock = threading.Lock()
            return cls._instance

    def subscribe(self, event_type: EventType, listener: Callable[[Event], None]) -> None:
        """Subscribe a callback listener to an event type.

        Args:
            event_type: EventType enum value
            listener: Callable function taking Event parameter
        """
        with self._sub_lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            if listener not in self._subscribers[event_type]:
                self._subscribers[event_type].append(listener)

    def unsubscribe(self, event_type: EventType, listener: Callable[[Event], None]) -> bool:
        """Unsubscribe a listener from an event type.

        Args:
            event_type: EventType enum value
            listener: Callback listener to remove

        Returns:
            True if removed, False otherwise
        """
        with self._sub_lock:
            if event_type in self._subscribers and listener in self._subscribers[event_type]:
                self._subscribers[event_type].remove(listener)
                return True
            return False

    def publish(self, event_type: EventType, data: Any = None) -> None:
        """Publish an event to all subscribed listeners.

        Args:
            event_type: EventType enum value
            data: Data payload associated with event
        """
        event = Event(event_type, data)
        with self._sub_lock:
            listeners = self._subscribers.get(event_type, []).copy()

        for listener in listeners:
            try:
                listener(event)
            except Exception as e:
                print(f"Error in event listener for {event_type}: {e}")

    def clear(self) -> None:
        """Clear all event subscribers."""
        with self._sub_lock:
            self._subscribers.clear()
