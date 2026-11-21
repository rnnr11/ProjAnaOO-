import argparse
import sys
from collections.abc import Callable, Sequence
from Agente.conversation import UnexpectedModelOutputError, ModelExecutionError, EmptyQuestionError, Conversation

def run_flow(question: str, conversation_history: str) -> str:
    from Flow.flow_config import FlowConfig

    flow = FlowConfig()
    try:
        flow.state.input_text = question
        flow.state.history_text = conversation_history
        flow.kickoff()
        answer = flow.state.output_text
    except (
        ConnectionError,
        TimeoutError,
    ) as exc:
        raise ModelExecutionError(
            "Não foi possível consultar o modelo local. "
            "Verifique se o Ollama está em execução e se o modelo configurado está disponível."
        ) from exc

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
    conversation = Conversation(run_flow)

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
