import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.initialization import initialize_components
from src.health_checks import run_health_checks


class TestHealthChecks(unittest.TestCase):

    def test_run_health_checks(self):
        """Test diagnostic health check report generation."""
        components, _ = initialize_components()
        report = run_health_checks(components)

        self.assertEqual(report["status"], "healthy")
        self.assertEqual(report["components"]["audio_pipeline"]["status"], "ok")
        self.assertEqual(report["components"]["wake_detector"]["status"], "ok")
        self.assertEqual(report["components"]["stt_engine"]["status"], "ok")

    def test_unhealthy_report(self):
        """Test health check report when component is missing."""
        incomplete_components = {}
        report = run_health_checks(incomplete_components)
        self.assertEqual(report["status"], "unhealthy")


if __name__ == '__main__':
    unittest.main()
