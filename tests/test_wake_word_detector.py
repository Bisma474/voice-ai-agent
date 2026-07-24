import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.wake_word_detector import WakeWordDetector


class TestWakeWordDetector(unittest.TestCase):

    def setUp(self):
        self.detector = WakeWordDetector(sensitivity=0.5)

    def test_start_stop_listening(self):
        """Test listening state control."""
        self.assertFalse(self.detector.is_listening())
        self.detector.start_listening()
        self.assertTrue(self.detector.is_listening())
        self.detector.stop_listening()
        self.assertFalse(self.detector.is_listening())

    def test_wake_words_management(self):
        """Test sensitivity and adding wake words."""
        self.detector.set_sensitivity(0.8)
        self.detector.add_wake_word("computer", sensitivity=0.7)
        self.assertIn("computer", self.detector.get_wake_words())

    def test_detection_callback(self):
        """Test wake word detection trigger."""
        detected_words = []

        def callback(word):
            detected_words.append(word)

        self.detector.set_detection_callback(callback)
        self.detector.start_listening()

        frame_normal = b'NORMAL_AUDIO_FRAME'
        result1 = self.detector.process_audio_frame(frame_normal)
        self.assertFalse(result1)
        self.assertEqual(len(detected_words), 0)

        frame_wake = b'AUDIO_DATA_WITH_WAKE_WORD'
        result2 = self.detector.process_audio_frame(frame_wake)
        self.assertTrue(result2)
        self.assertEqual(len(detected_words), 1)


if __name__ == '__main__':
    unittest.main()
