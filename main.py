from crewai import LLM

# Execução
llm = LLM(model='ollama/qwen2.5:7b',
base_url='http://localhost:11434')
print(llm.call('Diga oi em duas frases'))