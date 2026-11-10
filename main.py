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
    print(run_crew(crew, "Explique o que é o padrão Facade e qual problema ele resolve.")) # trocar "Olá" para a pergunta desejada
    

if __name__ == "__main__":
    main()