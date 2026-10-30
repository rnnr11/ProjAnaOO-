import sys
import os

sys.path.append(os.path.abspath('./Crew'))

from Crew.crew import crewInit

# Execução
def run_crew(crew, question: str) -> str:
    reply = crew.kickoff(inputs={"question": question})
    return reply.raw


def main():
    crew = crewInit()
    print(run_crew(crew, "Qual a diferença entre uma classe abstrata e uma interface em Java?")) # trocar "Olá" para a pergunta desejada
    

if __name__ == "__main__":
    main()