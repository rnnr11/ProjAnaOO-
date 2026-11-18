from pathlib import Path
from crewai import Agent, Task, Crew, Process, LLM
import yaml

def agents_init():
    current_dir = Path(__file__).resolve().parent

    tutor = agent_init(current_dir / "agents" / "tutor_config.yaml")
    domain_expert = agent_init(current_dir / "agents" / "expert_config.yaml")
    validator = agent_init(current_dir / "agents" / "validator_config.yaml")
    analyzer = agent_init(current_dir / "agents" / "analyzer_config.yaml")

    return {
            "tutor": tutor, 
            "domain_expert": domain_expert,
            "validator": validator,
            "analyzer": analyzer
    }

agents = agents_init()
current_dir = Path(__file__).resolve().parent

llm = LLM(
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

def talking_crew_init(): # por fazer
    return crew_config(agents=list(agents.values()), tasks=[])

def expert_crew_init():
    read_question = task_init(current_dir / "tasks" / "expert_crew" / "read_question.yaml", context=[], agent=agents["analyzer"])
    expert_reply = task_init(current_dir / "tasks" / "expert_crew" / "expert_reply.yaml", context=[read_question], agent=agents["domain_expert"])
    tutor_reply = task_init(current_dir / "tasks" / "expert_crew" / "tutor_reply.yaml", context=[expert_reply], agent=agents["tutor"])
    validate_reply = task_init(current_dir / "tasks" / "expert_crew" / "validate.yaml", context=[tutor_reply], agent=agents["validator"])

    tasks = [read_question, expert_reply, tutor_reply, validate_reply]

    return crew_config(agents=list(agents.values()), tasks=tasks)