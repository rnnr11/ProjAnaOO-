import sys
import os

sys.path.append(os.path.abspath('./Flow'))

from Flow.flow_config import FlowConfig

# Execução
def main():

    # Inicializa o fluxo
    my_flow = FlowConfig()
    my_flow.state.input_text = "Olá, tudo bem? Gostaria de um exemplo do padrão facade." # Insira a pergunta aqui
    my_flow.kickoff()
    print(my_flow.state.output_text)
    

if __name__ == "__main__":
    main()