import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def load_yaml(relative_path):
    with (ROOT / relative_path).open(encoding="utf-8") as file:
        return yaml.safe_load(file)


class PromptTests(unittest.TestCase):
    def test_all_agents_are_scoped_to_facade_and_anti_hallucination(self):
        agent_paths = (
            "Crew/agents/analyzer_config.yaml",
            "Crew/agents/expert_config.yaml",
            "Crew/agents/tutor_config.yaml",
            "Crew/agents/validator_config.yaml",
        )

        for path in agent_paths:
            with self.subTest(path=path):
                agent = load_yaml(path)
                prompt = " ".join(
                    (agent["role"], agent["goal"], agent["backstory"])
                ).casefold()
                self.assertIn("facade", prompt)
                self.assertTrue(
                    "não invent" in prompt
                    or "não introduza fatos sem suporte" in prompt
                )

    def test_tasks_receive_conversation_context_and_apply_learning_flow(self):
        read_question = load_yaml("Crew/tasks/read_question.yaml")
        tutor_reply = load_yaml("Crew/tasks/tutor_reply.yaml")
        validate = load_yaml("Crew/tasks/validate.yaml")

        self.assertIn("{question}", read_question["description"])
        self.assertIn("{conversation_history}", read_question["description"])
        self.assertIn("{question}", tutor_reply["description"])
        self.assertIn("{conversation_history}", tutor_reply["description"])
        self.assertIn("peça que o estudante tente", tutor_reply["description"])
        self.assertIn("{conversation_history}", validate["description"])
        self.assertIn("padrões ou fatos", validate["description"])

    def test_ollama_endpoint_supports_local_cli_and_compose_network(self):
        crew_source = (ROOT / "Crew/crew.py").read_text(encoding="utf-8")
        compose = load_yaml("compose.yaml")

        self.assertIn(
            'os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")',
            crew_source,
        )
        self.assertIn(
            'timeout=int(os.getenv("OLLAMA_REQUEST_TIMEOUT", "600"))',
            crew_source,
        )
        self.assertEqual(
            compose["services"]["crewai"]["environment"]["OLLAMA_BASE_URL"],
            "http://ollama:11434/v1",
        )
        self.assertEqual(
            compose["services"]["crewai"]["environment"]["OLLAMA_REQUEST_TIMEOUT"],
            "${OLLAMA_REQUEST_TIMEOUT:-600}",
        )
        self.assertEqual(
            compose["services"]["crewai"]["depends_on"]["ollama"]["condition"],
            "service_healthy",
        )


if __name__ == "__main__":
    unittest.main()
