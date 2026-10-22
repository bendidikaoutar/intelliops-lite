import unittest

from src.extraction import masquer_secrets, normaliser_log

LIGNE = "2026-10-05 10:02:11 ERROR backend OOMKilled restarts=14 password=abc123"


class TestExtraction(unittest.TestCase):
    def test_masquer_secrets(self):
        self.assertEqual(
            masquer_secrets("user=bob password=abc123"),
            "user=bob password=[SECRET]"
        )

    def test_normaliser_log(self):
        evt = normaliser_log(LIGNE, 42)
        self.assertEqual(evt.id, "EVT-00042")
        self.assertEqual(evt.timestamp, "2026-10-05T10:02:11Z")
        self.assertEqual(evt.severity, "HIGH")
        self.assertNotIn("abc123", evt.message)
    def test_bearer(self):
        self.assertEqual(masquer_secrets("Authorization: Bearer eyJ.abc-1"),
                         "Authorization: Bearer [SECRET]")


if __name__ == "__main__":
    unittest.main()