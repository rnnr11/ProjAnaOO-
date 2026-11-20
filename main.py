import sys
import os

sys.path.append(os.path.abspath('./Flow'))

from Flow.flow_config import FlowConfig

# Execução
def main():

    # Inicializa o fluxo
    my_flow = FlowConfig()
    my_flow.state.input_text = "Você gostaria de aprender sobre o padrão facade?" # Insira a pergunta aqui
    my_flow.kickoff()
    print(my_flow.state.output_text)
    

if __name__ == "__main__":
    main()