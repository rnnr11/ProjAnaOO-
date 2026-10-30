# ProjAnaOO

Projeto Python desenvolvido com **CrewAI**, utilizando agentes de inteligência artificial para analisar perguntas, elaborar explicações técnicas e validar respostas. O modelo de linguagem é executado localmente através do **Ollama**, utilizando o Qwen 2.5 7B.

Toda a aplicação é executada em containers Docker, mantendo o ambiente isolado do sistema operacional hospedeiro.

## Tecnologias utilizadas

- **Python 3.12** — linguagem principal.
- **CrewAI** — gerenciamento e orquestração dos agentes.
- **Ollama** — execução local do modelo de linguagem.
- **Qwen 2.5 7B** — modelo utilizado pelos agentes.
- **Docker** — isolamento e execução dos serviços.
- **Docker Compose** — gerenciamento dos containers e da comunicação entre eles.

## Estrutura do projeto

```text
ProjAnaOO/
│
├── main.py
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── .dockerignore
│
└── Crew/
    ├── __init__.py
    ├── crew.py
    │
    ├── agents/
    │   ├── tutor.yaml
    │   ├── domain_expert.yaml
    │   ├── validator.yaml
    │   └── analyzer.yaml
    │
    └── tasks/
        ├── ...
```

- `main.py`: ponto de entrada da aplicação.
- `Crew/crew.py`: inicialização do CrewAI, configuração do LLM e montagem dos agentes e tarefas.
- `Crew/agents/`: arquivos YAML com as configurações dos agentes.
- `Crew/tasks/`: arquivos YAML com as definições das tarefas.
- `Dockerfile`: definição da imagem Python utilizada pela aplicação.
- `compose.yaml`: configuração dos serviços Docker e da rede interna.
- `requirements.txt`: dependências Python.

## Pré-requisitos

Antes de executar o projeto, instale:

1. [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2. WSL 2 habilitado, caso esteja utilizando Windows.
3. Docker Compose disponível pelo comando `docker compose`.

Não é necessário instalar Python ou Ollama diretamente no Windows para executar a aplicação pelo Docker.

Certifique-se de que o Docker Desktop esteja aberto e funcionando.

Para verificar a instalação:

```powershell
docker --version
docker compose version
```

## 1. Clonar o repositório

Clone o projeto e entre na pasta:

```powershell
git clone https://github.com/rnnr11/ProjAnaOO-.git
cd ProjAnaOO
```

Caso já tenha o projeto em sua máquina, basta abrir o terminal na pasta raiz.

## 2. Configurar o modelo Ollama

O projeto utiliza o modelo `qwen2.5:7b`, executado no container Ollama.

A configuração de infraestrutura utiliza um volume Docker persistente chamado `ollama_data`, responsável por armazenar os modelos baixados.

Crie o volume:

```powershell
docker volume create ollama_data
```

**Importante:** o volume deve ter exatamente esse nome, pois o `compose.yaml` utiliza um volume externo chamado `ollama_data`.

## 3. Construir e iniciar o Ollama

Na raiz do projeto, execute:

```powershell
docker compose up -d ollama
```

Esse comando inicia o serviço Ollama em segundo plano.

Confira se o container está em execução:

```powershell
docker compose ps
```

## 4. Baixar o modelo

Execute o comando abaixo para baixar o modelo utilizado pelo projeto:

```powershell
docker compose exec ollama ollama pull qwen2.5:7b
```

O download é necessário apenas na primeira execução ou quando o modelo ainda não estiver presente no volume.

Para verificar os modelos disponíveis:

```powershell
docker compose exec ollama ollama list
```

O resultado esperado deve conter:

```text
NAME          ID              SIZE
qwen2.5:7b    ...             4.7 GB
```

Também é possível testar o funcionamento do modelo:

```powershell
docker compose exec ollama ollama run qwen2.5:7b "Responda apenas OK"
```

A resposta esperada é:

```text
OK
```

## 5. Configuração do LLM no CrewAI

No arquivo `Crew/crew.py`, o modelo deve utilizar o endpoint compatível com a API da OpenAI disponibilizado pelo Ollama.

A configuração esperada é:

```python
from crewai import LLM

llm = LLM(
    model="qwen2.5:7b",
    base_url="http://ollama:11434/v1",
    api_key="ollama",
    custom_openai=True,
    temperature=0.5,
    timeout=300,
)
```

**Atenção:** utilize `ollama` como hostname, e não `localhost`.

Como os serviços estão em containers diferentes, o nome do serviço definido no Docker Compose é utilizado para a comunicação entre eles.

O parâmetro `custom_openai=True` permite utilizar a integração OpenAI personalizada do CrewAI com o endpoint compatível do Ollama.

## 6. Construir a aplicação CrewAI

Com o Ollama iniciado e o modelo disponível, construa a imagem da aplicação:

```powershell
docker compose build crewai
```

Esse comando instala as dependências definidas em `requirements.txt` e copia os arquivos do projeto para a imagem.

Sempre que modificar o código Python, os arquivos YAML ou as dependências, reconstrua a imagem:

```powershell
docker compose build crewai
```

Para forçar uma reconstrução sem utilizar o cache:

```powershell
docker compose build --no-cache crewai
```

## 7. Executar o projeto

Com os serviços configurados, execute:

```powershell
docker compose run --rm crewai
```

Esse comando:

1. Cria um container temporário para a aplicação.
2. Mantém o Ollama em execução.
3. Executa o arquivo `main.py`.
4. Inicializa os agentes e suas respectivas tarefas.
5. Exibe os resultados no terminal.
6. Remove o container temporário ao finalizar.

A opção `--rm` remove o container da aplicação após sua execução, sem excluir a imagem ou o volume persistente do Ollama.

## 8. Alterar a pergunta enviada aos agentes

A pergunta inicial é definida em `main.py`.

Exemplo:

```python
from Crew.crew import crewInit

def run_crew(crew, question: str) -> str:
    reply = crew.kickoff(inputs={"question": question})
    return reply.raw

def main():
    crew = crewInit()
    print(run_crew(
        crew,
        "Qual a diferença entre uma classe abstrata e uma interface em Java?"
    ))

if __name__ == "__main__":
    main()
```

Altere o texto passado para `run_crew()` para enviar uma nova pergunta aos agentes.

Após modificar o código, execute novamente:

```powershell
docker compose build crewai
docker compose run --rm crewai
```

## 9. Encerrar os serviços

Para encerrar os containers:

```powershell
docker compose down
```

Esse comando interrompe e remove os containers e a rede criada pelo Compose.

**O volume `ollama_data` não é removido**, portanto os modelos baixados permanecem disponíveis nas próximas execuções.

Não utilize `docker compose down -v` caso queira preservar os modelos.

## Arquitetura da execução

A aplicação utiliza dois serviços principais:

```text
                  Docker Compose
                        |
              Rede Docker interna
                 (isolated)
                        |
             +----------+----------+
             |                     |
             v                     v
      +-------------+       +-------------+
      |   CrewAI    | ----> |   Ollama    |
      |             | HTTP  |             |
      | Python 3.12 |       | Qwen 2.5 7B |
      +-------------+       +-------------+
                                  |
                                  v
                           Volume persistente
                             ollama_data
```

O container CrewAI realiza as chamadas HTTP para o serviço Ollama pela rede interna do Docker.

A rede é configurada como interna (`internal: true`), evitando que os containers tenham acesso direto à rede externa através dessa rede.

O modelo permanece armazenado no volume Docker, evitando downloads a cada execução.

## Segurança e isolamento

A configuração dos containers aplica algumas restrições:

- Execução da aplicação com usuário não privilegiado.
- Sistema de arquivos somente leitura (`read_only`).
- Permissões Linux adicionais removidas (`cap_drop: ALL`).
- Proteção contra elevação de privilégios (`no-new-privileges`).
- Limites de memória e CPU.
- Limites de processos (`pids_limit`).
- Diretório temporário disponibilizado por `tmpfs`.
- Comunicação entre os serviços por uma rede Docker interna.

Essas medidas reduzem a superfície de ataque e limitam os recursos disponíveis aos containers.

**Observação:** o isolamento Docker não equivale a uma máquina virtual ou a uma sandbox de segurança absoluta. Para executar código não confiável, são necessárias medidas adicionais de proteção.

## Solução de problemas

### 1. Connection refused ao conectar com o Ollama

Erro:

```text
httpx.ConnectError: [Errno 111] Connection refused
```

Verifique se o container Ollama está em execução:

```powershell
docker compose ps
```

Confira os logs:

```powershell
docker compose logs ollama
```

Teste se o modelo está disponível:

```powershell
docker compose exec ollama ollama list
```

Teste a comunicação entre os containers:

```powershell
docker compose run --rm --entrypoint python crewai -c "import urllib.request; print(urllib.request.urlopen('http://ollama:11434/api/tags', timeout=5).read().decode())"
```

Se a requisição retornar informações dos modelos, a comunicação HTTP entre os containers está funcionando.

### 2. Modelo não encontrado

Caso o modelo não esteja disponível:

```powershell
docker compose exec ollama ollama pull qwen2.5:7b
```

### 3. Alterações no código não aparecem

Reconstrua a imagem da aplicação:

```powershell
docker compose build crewai
```

Em seguida:

```powershell
docker compose run --rm crewai
```

### 4. Verificar os logs do Ollama

```powershell
docker compose logs -f ollama
```

Para interromper a visualização dos logs, pressione `Ctrl + C`.

### 5. Volume não encontrado

Se o Docker informar que o volume externo não existe, crie-o:

```powershell
docker volume create ollama_data
```

Se você já possuía um volume anterior com outro nome e deseja preservar os modelos existentes, verifique os volumes disponíveis antes de criar ou substituir qualquer volume.

Liste os volumes:

```powershell
docker volume ls
```

Não remova volumes antigos sem confirmar que não contêm os modelos que deseja preservar.

---

## Resumo dos comandos

Após a configuração inicial, o fluxo normal de execução é:

```powershell
# Iniciar o Ollama
docker compose up -d ollama

# Construir a aplicação (necessário após alterações)
docker compose build crewai

# Executar o CrewAI
docker compose run --rm crewai

# Encerrar os serviços
docker compose down
```

O modelo é armazenado persistentemente no volume `ollama_data`, portanto não precisa ser baixado novamente a cada execução.
