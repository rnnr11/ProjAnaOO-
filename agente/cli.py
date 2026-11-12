import argparse
import sys
from collections.abc import Callable, Sequence


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
        self._turns: list[tuple[str, str]] = []

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


def run_crew(question: str, conversation_history: str) -> str:
    from litellm.exceptions import APIConnectionError, APIError, Timeout

    from Crew.crew import crewInit

    crew = crewInit()
    try:
        result = crew.kickoff(
            inputs={
                "question": question,
                "conversation_history": conversation_history,
            }
        )
    except (
        APIConnectionError,
        APIError,
        Timeout,
        ConnectionError,
        TimeoutError,
    ) as exc:
        raise ModelExecutionError(
            "Não foi possível consultar o modelo local. "
            "Verifique se o Ollama está em execução e se o modelo configurado está disponível."
        ) from exc

    answer = getattr(result, "raw", None)
    if not isinstance(answer, str) or not answer.strip():
        raise UnexpectedModelOutputError(
            "A execução terminou sem produzir uma resposta textual."
        )

    return answer


def main(
    argv: Sequence[str] | None = None,
    *,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
    error_fn: Callable[[str], None] | None = None,
) -> int:
    if error_fn is None:
        error_fn = lambda message: print(message, file=sys.stderr)

    parser = argparse.ArgumentParser(
        description="Tutor pedagógico local para o padrão Facade."
    )
    parser.add_argument(
        "question",
        nargs="?",
        help="pergunta para o tutor; sem argumento, inicia o chat interativo",
    )
    args = parser.parse_args(argv)
    conversation = Conversation(run_crew)

    if args.question is not None:
        try:
            output_fn(conversation.respond(args.question))
        except EmptyQuestionError as exc:
            error_fn(str(exc))
            return 2
        except (ModelExecutionError, UnexpectedModelOutputError) as exc:
            error_fn(str(exc))
            return 1
        return 0

    output_fn("Tutor do padrão Facade. Digite 'sair' para encerrar.")
    while True:
        try:
            question = input_fn("Você: ")
        except EOFError:
            output_fn("Conversa encerrada.")
            return 0

        if question.strip().casefold() == "sair":
            output_fn("Conversa encerrada.")
            return 0

        try:
            output_fn(f"Sistema: {conversation.respond(question)}")
        except EmptyQuestionError as exc:
            error_fn(str(exc))
        except (ModelExecutionError, UnexpectedModelOutputError) as exc:
            error_fn(str(exc))
