import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.event_system import EventBus, EventType, Event


class TestEventSystem(unittest.TestCase):

    def setUp(self):
        self.bus = EventBus()
        self.bus.clear()

    def test_publish_subscribe(self):
        """Test subscribing to and publishing events."""
        received_events = []

        def listener(event: Event):
            received_events.append(event)

        self.bus.subscribe(EventType.WAKE_WORD_DETECTED, listener)
        self.bus.publish(EventType.WAKE_WORD_DETECTED, "hey assistant")

        self.assertEqual(len(received_events), 1)
        self.assertEqual(received_events[0].type, EventType.WAKE_WORD_DETECTED)
        self.assertEqual(received_events[0].data, "hey assistant")

    def test_unsubscribe(self):
        """Test unsubscribing from events."""
        received_events = []

        def listener(event: Event):
            received_events.append(event)

        self.bus.subscribe(EventType.STATE_CHANGED, listener)
        self.bus.publish(EventType.STATE_CHANGED, "data1")
        self.assertEqual(len(received_events), 1)

        self.assertTrue(self.bus.unsubscribe(EventType.STATE_CHANGED, listener))
        self.bus.publish(EventType.STATE_CHANGED, "data2")
        self.assertEqual(len(received_events), 1)


if __name__ == '__main__':
    unittest.main()
