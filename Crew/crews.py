import os
from pathlib import Path
from crewai import Agent, Task, Crew, Process, LLM
import yaml

current_dir = Path(__file__).resolve().parent

llm = LLM(
    model='qwen2.5:7b',
    base_url=os.getenv("OLLAMA_BASE_URL", "http://ollama:11434/v1"),
    api_key= 'ollama',
    custom_openai=True,
    temperature=0.5,
    timeout=int(os.getenv("OLLAMA_REQUEST_TIMEOUT", "600")),
    )

# yaml
def extract_yaml(path):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return data

# Agent
def agent_config(role, goal, backstory):
    agent = Agent(role=role, goal=goal, backstory=backstory, verbose=True, allow_delegation=False, llm=llm)
    return agent

def agent_init(path):
    agent = agent_config(**extract_yaml(path))
    return agent

# Task
def task_config(description, expected_output, context, agent):
    task = Task(description=description, expected_output=expected_output, context=context, agent=agent)
    return task

def task_init(path, context, agent):
    task = task_config(**extract_yaml(path), context=context, agent=agent)
    return task

# Crew
def crew_config(agents, tasks):
    crew = Crew(agents=agents, tasks=tasks, process=Process.sequential)
    return crew

def talking_crew_init():
    chatty = agent_init(current_dir / "agents" / "talking_crew" / "chatty_config.yaml")
    agents = [chatty]

    generic_reply = task_init(current_dir / "tasks" / "talking_crew" / "generic_reply.yaml", context=[], agent=chatty)
    tasks = [generic_reply]

    return crew_config(agents=agents, tasks=tasks)

def expert_crew_init():
    tutor = agent_init(current_dir / "agents" / "expert_crew" / "tutor_config.yaml")
    domain_expert = agent_init(current_dir / "agents" / "expert_crew" / "expert_config.yaml")
    validator = agent_init(current_dir / "agents" / "expert_crew" / "validator_config.yaml")
    analyzer = agent_init(current_dir / "agents" / "expert_crew" / "analyzer_config.yaml")

    agents = [tutor, domain_expert, validator, analyzer]

    read_question = task_init(current_dir / "tasks" / "expert_crew" / "read_question.yaml", context=[], agent=analyzer)
    expert_reply = task_init(current_dir / "tasks" / "expert_crew" / "expert_reply.yaml", context=[read_question], agent=domain_expert)
    tutor_reply = task_init(current_dir / "tasks" / "expert_crew" / "tutor_reply.yaml", context=[expert_reply], agent=tutor)
    validate_reply = task_init(current_dir / "tasks" / "expert_crew" / "validate.yaml", context=[tutor_reply], agent=validator)

    tasks = [read_question, expert_reply, tutor_reply, validate_reply]

    return crew_config(agents=agents, tasks=tasks)