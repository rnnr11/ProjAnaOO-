# ProjAnaOO

Tutor pedagógico local sobre o padrão Facade e orientação a objetos. A aplicação usa um fluxo CrewAI para classificar perguntas, encaminhá-las aos agentes apropriados e elaborar uma resposta com um modelo servido pelo Ollama. Também pode ser executada em containers com Docker Compose.

## Tecnologias

- Python 3.12
- CrewAI 1.15.41
- Ollama com o modelo `qwen2.5:7b`
- Docker e Docker Compose (opcionais para execução local)

## Estrutura do projeto

```text
ProjAnaOO-/
├── src/
│   ├── agente/                 # CLI e fluxo de conversa
│   ├── Crew/                   # Agentes, tarefas e configuração do CrewAI
│   └── Flow/                   # Fluxo de classificação e roteamento
├── tests/
├── main.py                     # Ponto de entrada alternativo
├── pyproject.toml              # Configuração do pacote src
├── requirements.txt
├── Dockerfile
└── compose.yaml
```

Os arquivos YAML de agentes e tarefas ficam em `src/Crew/agents/` e `src/Crew/tasks/`.

## Execução local no Windows

### Pré-requisitos

- Python 3.12
- [Ollama](https://ollama.com/) instalado e em execução no computador

### Preparar o ambiente Python

Na raiz do repositório, crie e ative um ambiente virtual e instale as dependências e o pacote:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
```

A instalação editável registra os pacotes que estão em `src/`, permitindo executar `python -m agente` a partir da raiz.

### Preparar o Ollama

Baixe o modelo configurado e confirme que ele está disponível:

```powershell
ollama pull qwen2.5:7b
ollama list
```

O endereço padrão usado pela aplicação é `http://localhost:11434/v1`. Para usar outro endereço ou alterar o timeout, configure:

```powershell
$env:OLLAMA_BASE_URL = "http://localhost:11434/v1"
$env:OLLAMA_REQUEST_TIMEOUT = "600"
```

`OLLAMA_REQUEST_TIMEOUT` é informado em segundos. O valor padrão é `600`.

### Executar

Uma pergunta:

```powershell
python -m agente "Explique o padrão Facade com um exemplo pequeno em Java."
```

Chat interativo com histórico durante a sessão:

```powershell
python -m agente
```

Digite `sair` para encerrar o chat. `main.py` também pode ser usado como entrada alternativa com `python main.py`.

## Execução com Docker Compose

Pré-requisitos: Docker Desktop (no Windows, com WSL 2 habilitado) e Docker Compose.

O Compose usa o volume externo `ollama_data` para preservar os modelos entre execuções. Crie-o uma vez:

```powershell
docker volume create ollama_data
```

Inicie o Ollama, baixe o modelo no container e construa a imagem da aplicação:

```powershell
docker compose up -d ollama
docker compose exec ollama ollama pull qwen2.5:7b
docker compose build crewai
```

Execute uma pergunta ou inicie o chat:

```powershell
docker compose run --rm crewai "Explique o padrão Facade com um exemplo pequeno em Java."
docker compose run --rm crewai
```

O serviço `crewai` usa `http://ollama:11434/v1` para se comunicar com o serviço Ollama pela rede interna do Compose. O timeout pode ser alterado em `.env` com `OLLAMA_REQUEST_TIMEOUT`, ou diretamente no ambiente do processo. Após mudar o código, os arquivos YAML ou as dependências, reconstrua a imagem:

```powershell
docker compose build crewai
```

Para parar e remover os containers e a rede do Compose:

```powershell
docker compose down
```

Esse comando preserva o volume `ollama_data`. Evite `docker compose down -v` se quiser manter os modelos baixados.

## Testes

Com as dependências instaladas e o pacote registrado no ambiente virtual:

```powershell
python -m unittest discover -s tests -v
```

## Solução de problemas

### Falha ao conectar com o Ollama

Confirme que o Ollama está em execução e que o endpoint de modelos responde:

```powershell
Invoke-RestMethod http://localhost:11434/v1/models
```

Se necessário, baixe o modelo e confirme a variável de endereço:

```powershell
ollama pull qwen2.5:7b
$env:OLLAMA_BASE_URL = "http://localhost:11434/v1"
```

Na execução com Docker, verifique os serviços e os logs:

```powershell
docker compose ps
docker compose logs ollama
```

Dentro do Compose, use o hostname `ollama`; `localhost` apontaria para o próprio container da aplicação.

### Timeout durante a geração

O primeiro carregamento do modelo e a geração em computadores com recursos limitados podem demorar. Aumente o timeout, por exemplo:

```powershell
$env:OLLAMA_REQUEST_TIMEOUT = "900"
```

## Isolamento do Docker

O Compose configura usuário não privilegiado para a aplicação, sistema de arquivos somente leitura, remoção de capabilities, limite de recursos e rede interna para a comunicação entre CrewAI e Ollama. Essas medidas reduzem a exposição, mas não equivalem a uma máquina virtual nem a uma sandbox de segurança absoluta.
