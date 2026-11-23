import unittest
from unittest.mock import patch

from agente.cli import (
    Conversation,
    EmptyQuestionError,
    ModelExecutionError,
    UnexpectedModelOutputError,
    main,
)


class ConversationTests(unittest.TestCase):
    def test_passes_prior_turns_and_stores_only_successful_answers(self):
        calls = []

        def runner(question, history):
            calls.append((question, history))
            return f"Resposta {len(calls)}"

        conversation = Conversation(runner)
        self.assertEqual(conversation.respond("O que é Facade?"), "Resposta 1")
        self.assertEqual(conversation.respond("E quando evitar?"), "Resposta 2")

        self.assertEqual(calls[0][1], "Nenhuma interação anterior.")
        self.assertIn("Estudante: O que é Facade?", calls[1][1])
        self.assertIn("Tutor: Resposta 1", calls[1][1])

    def test_rejects_empty_question_without_calling_runner(self):
        runner = unittest.mock.Mock()
        conversation = Conversation(runner)

        with self.assertRaises(EmptyQuestionError):
            conversation.respond(" \t ")

        runner.assert_not_called()

    def test_rejects_empty_output_without_adding_to_history(self):
        calls = []

        def runner(question, history):
            calls.append(history)
            return " " if len(calls) == 1 else "Resposta"

        conversation = Conversation(runner)
        with self.assertRaises(UnexpectedModelOutputError):
            conversation.respond("Primeira pergunta")

        conversation.respond("Nova pergunta")
        self.assertEqual(calls[1], "Nenhuma interação anterior.")


class CliTests(unittest.TestCase):
    def test_one_shot_question_prints_answer(self):
        output = []
        errors = []

        with patch("agente.cli.run_crew", return_value="Resposta do tutor"):
            result = main(
                ["Explique Facade"],
                output_fn=output.append,
                error_fn=errors.append,
            )

        self.assertEqual(result, 0)
        self.assertEqual(output, ["Resposta do tutor"])
        self.assertEqual(errors, [])

    def test_one_shot_empty_question_returns_error(self):
        output = []
        errors = []

        with patch("agente.cli.run_crew") as runner:
            result = main(["   "], output_fn=output.append, error_fn=errors.append)

        self.assertEqual(result, 2)
        self.assertEqual(output, [])
        self.assertEqual(errors, ["A pergunta não pode estar vazia."])
        runner.assert_not_called()

    def test_interactive_mode_preserves_conversation_history(self):
        output = []
        errors = []
        prompts = iter(["Explique Facade", "Quando evitar?", "sair"])
        calls = []

        def runner(question, history):
            calls.append((question, history))
            return f"Resposta {len(calls)}"

        with patch("agente.cli.run_crew", side_effect=runner):
            result = main(
                [],
                input_fn=lambda prompt: next(prompts),
                output_fn=output.append,
                error_fn=errors.append,
            )

        self.assertEqual(result, 0)
        self.assertEqual(len(calls), 2)
        self.assertIn("Tutor: Resposta 1", calls[1][1])
        self.assertIn("Sistema: Resposta 2", output)
        self.assertEqual(errors, [])

    def test_model_failure_is_reported_without_traceback(self):
        output = []
        errors = []

        with patch(
            "agente.cli.run_crew",
            side_effect=ModelExecutionError("Falha no modelo local."),
        ):
            result = main(
                ["Explique Facade"],
                output_fn=output.append,
                error_fn=errors.append,
            )

        self.assertEqual(result, 1)
        self.assertEqual(output, [])
        self.assertEqual(errors, ["Falha no modelo local."])

    def test_unexpected_model_output_is_reported(self):
        output = []
        errors = []

        with patch("agente.cli.run_crew", return_value=""):
            result = main(
                ["Explique Facade"],
                output_fn=output.append,
                error_fn=errors.append,
            )

        self.assertEqual(result, 1)
        self.assertEqual(output, [])
        self.assertEqual(
            errors, ["O sistema não produziu uma resposta textual."]
        )

    def test_interactive_empty_question_is_reported_and_chat_continues(self):
        output = []
        errors = []
        prompts = iter([" ", "O que é Facade?", "sair"])

        with patch("agente.cli.run_crew", return_value="Resposta"):
            result = main(
                [],
                input_fn=lambda prompt: next(prompts),
                output_fn=output.append,
                error_fn=errors.append,
            )

        self.assertEqual(result, 0)
        self.assertEqual(errors, ["A pergunta não pode estar vazia."])
        self.assertIn("Sistema: Resposta", output)


if __name__ == "__main__":
    unittest.main()
