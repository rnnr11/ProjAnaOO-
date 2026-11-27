import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def load_yaml(relative_path):
    with (ROOT / relative_path).open(encoding="utf-8") as file:
        return yaml.safe_load(file)


class PromptTests(unittest.TestCase):
    def test_agent_configs_have_the_expected_roles(self):
        expected_roles = {
            "analyzer_config.yaml": "doutor em pedagogia",
            "expert_config.yaml": "especialista em projeto orientado a objetos",
            "tutor_config.yaml": "tutor pedagógico",
            "validator_config.yaml": "analista sênior",
        }

        for filename, expected_role in expected_roles.items():
            path = f"src/Crew/agents/expert_crew/{filename}"
            with self.subTest(path=path):
                agent = load_yaml(path)
                self.assertIn(expected_role, agent["role"].casefold())
                self.assertTrue(agent["goal"].strip())
                self.assertTrue(agent["backstory"].strip())

    def test_tasks_define_question_analysis_teaching_and_validation(self):
        read_question = load_yaml("src/Crew/tasks/expert_crew/read_question.yaml")
        tutor_reply = load_yaml("src/Crew/tasks/expert_crew/tutor_reply.yaml")
        validate = load_yaml("src/Crew/tasks/expert_crew/validate.yaml")

        self.assertIn("{question}", read_question["description"])
        self.assertIn("explicação didática", tutor_reply["description"].casefold())
        self.assertIn("corrija inconsistências", validate["description"].casefold())
        self.assertIn("markdown", validate["expected_output"].casefold())

    def test_ollama_endpoint_supports_local_cli_and_compose_network(self):
        crew_source = (ROOT / "src/Crew/crews.py").read_text(encoding="utf-8")
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
