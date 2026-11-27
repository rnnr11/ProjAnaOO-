from collections.abc import Callable
from collections import deque

Runner = Callable[[str, str], str]

class EmptyQuestionError(ValueError):
    pass


class ModelExecutionError(RuntimeError):
    pass


class UnexpectedModelOutputError(RuntimeError):
    pass


class Conversation:
    def __init__(self, runner: Runner):
        self._runner = runner
        self._turns: deque[tuple[str, str]] = deque(maxlen=3)

    def respond(self, question: str) -> str:
        if not question.strip():
            raise EmptyQuestionError("A pergunta não pode estar vazia.")

        history = self._format_history()
        answer = self._runner(question, history)
        if not isinstance(answer, str) or not answer.strip():
            raise UnexpectedModelOutputError(
                "O sistema não produziu uma resposta textual."
            )

        self._turns.append((question, answer))
        return answer

    def _format_history(self) -> str:
        if not self._turns:
            return "Nenhuma interação anterior."

        return "\n\n".join(
            f"Estudante: {question}\nTutor: {answer}"
            for question, answer in self._turns
        )