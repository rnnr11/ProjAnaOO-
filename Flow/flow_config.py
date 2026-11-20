from click import prompt
from crewai.flow.flow import Flow, start, router, listen
from crewai.llm import LLM
from pydantic import BaseModel

choice_llm = LLM(
    model='qwen2.5:7b',
    base_url='http://ollama:11434/v1',
    api_key= 'ollama',
    custom_openai=True,
    temperature=0.0,
)

def run_crew(crew, question: str, history: str) -> str:
    reply = crew.kickoff(inputs={"question": question, "history": history})
    return reply.raw

class FlowState(BaseModel):
     input_text: str = ""
     history_text: str = ""
     output_text: str = ""

class FlowConfig(Flow[FlowState]):
    @start()
    def read_input(self):
        return self.state.input_text

    @router(read_input)
    def filter_question(self):
        message = self.state.input_text.lower()

        prompt = f"""
            Você receberá uma mensagem e deverá classificá-la em uma das quatro categorias: CONVERSA, SOLUCAO, INVENCAO ou PERGUNTA.
            CONVERSA: Saudações, bate-papo, outras conversas que mencionem, mas não apresentem dúvidas sobre facade e OO, perguntas que não tenham a ver com o Facade ou OO. 
            (Ex: "Olá, como você está?", "Imite uma galinha", "Você gosta do padrão facade?", "Ontem estudei polimorfismo!", "Gostaria de aprender sobre facade?")
            SOLUCAO: Pedido de solução pronta para um problema do aluno, respostas de serviço. 
            (Ex: "Crie uma implementação do padrão facade para mim", "Me dê a resposta do exercício 3", "Implemente um facade para um sistema de banco de dados")
            INVENCAO: Pedido para inventar conceitos técnicos que não existem. 
            (Ex: "Invente um novo padrão de projeto", "Crie uma nova linguagem de programação")
            PERGUNTA: Perguntas técnicas sobre o padrão facade ou orientação a objetos. 
            (Ex: "Como o padrão facade ajuda a reduzir complexidade do sistema?", "O que é polimorfismo?", Quais são os outros pilares da orientação a objetos?", "Qual é a diferença entre o padrão facade e o padrão adapter?", "Me dê um exemplo qualquer do padrão Facade")

            Leia a mensagem e responda APENAS com UMA das palavras:
            CONVERSA, SOLUCAO, INVENCAO ou PERGUNTA.
            NÃO explique, NÃO diga "a resposta é", APENAS devolva a palavra.

            Mensagem recebida: "{message}"
            """
        
        response = choice_llm.call(
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        if "SOLUCAO" in response:
           return "SOLUCAO"
        elif "INVENCAO" in response: 
           return "INVENCAO"
        elif "PERGUNTA" in response:
           return "PERGUNTA"
        
        return "CONVERSA"

    @listen("CONVERSA")
    def conversation(self):
        from Crew.crews import talking_crew_init
        crew = talking_crew_init()
        self.state.output_text = run_crew(crew, self.state.input_text, self.state.history_text)

    @listen("SOLUCAO")
    def deny_solution(self):
        self.state.output_text = "Não posso fornecer soluções prontas. Explique suas dúvidas para que eu possa te ajudar!"

    @listen("INVENCAO")
    def deny_invention(self):
        self.state.output_text = "Não posso inventar conceitos técnicos que não existem. Estamos estudando a realidade! Por favor, vamos nos ater ao conteúdo."

    @listen("PERGUNTA")
    def question(self):
        from Crew.crews import expert_crew_init
        crew = expert_crew_init()
        self.state.output_text = run_crew(crew, self.state.input_text, self.state.history_text)