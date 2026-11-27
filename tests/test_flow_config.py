import os
import unittest

from Flow.flow_config import choice_llm


class FlowConfigTests(unittest.TestCase):
    def test_classifier_uses_configured_local_ollama_endpoint(self):
        expected_base_url = os.getenv(
            "OLLAMA_BASE_URL", "http://localhost:11434/v1"
        )
        expected_timeout = int(os.getenv("OLLAMA_REQUEST_TIMEOUT", "600"))

        self.assertEqual(choice_llm.base_url, expected_base_url)
        self.assertEqual(choice_llm.timeout, expected_timeout)


if __name__ == "__main__":
    unittest.main()
