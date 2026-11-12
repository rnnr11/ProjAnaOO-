from pathlib import Path
from crewai import Agent, Task, Crew, Process, LLM
import yaml

llm = llm = LLM(
    model='qwen2.5:7b',
    base_url='http://ollama:11434/v1',
    api_key= 'ollama',
    custom_openai=True,
    temperature=0.5,
    timeout=500
    )

# yaml
def extract_yaml(path):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return data

# Agent
def agentConfig(role, goal, backstory):
    agent = Agent(role=role, goal=goal, backstory=backstory, verbose=True, allow_delegation=False, llm=llm)
    return agent

def agentInit(path):
    agent = agentConfig(**extract_yaml(path))
    return agent

# Task
def taskConfig(description, expected_output, context, agent):
    task = Task(description=description, expected_output=expected_output, context=context, agent=agent)
    return task

def taskInit(path, context, agent):
    task = taskConfig(**extract_yaml(path), context=context, agent=agent)
    return task

# Crew
def crewConfig(agents, tasks):
    crew = Crew(agents=agents, tasks=tasks, process=Process.sequential)
    return crew

def crewInit():
    current_dir = Path(__file__).resolve().parent

    tutor = agentInit(current_dir / "agents" / "tutor_config.yaml")
    domain_expert = agentInit(current_dir / "agents" / "expert_config.yaml")
    validator = agentInit(current_dir / "agents" / "validator_config.yaml")
    analyzer = agentInit(current_dir / "agents" / "analyzer_config.yaml")

    read_question = taskInit(current_dir / "tasks" / "read_question.yaml", context=[], agent=analyzer)
    expert_reply = taskInit(current_dir / "tasks" / "expert_reply.yaml", context=[read_question], agent=domain_expert)
    tutor_reply = taskInit(current_dir / "tasks" / "tutor_reply.yaml", context=[expert_reply], agent=tutor)
    validate_reply = taskInit(current_dir / "tasks" / "validate.yaml", context=[tutor_reply], agent=validator)

    agents = [tutor, domain_expert, validator, analyzer]
    tasks = [read_question, expert_reply, tutor_reply, validate_reply]

    return crewConfig(agents=agents, tasks=tasks)