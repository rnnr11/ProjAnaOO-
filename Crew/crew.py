from crewai import Agent, Task, Crew, Process, LLM
import yaml

llm = llm = LLM(
    model='ollama/qwen2.5:7b',
    base_url='http://localhost:11434',
    temperature=0.5,
    timeout=300
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
    tutor = agentInit("Crew/agents/tutor_config.yaml")
    domain_expert = agentInit("Crew/agents/domain_expert_config.yaml")
    validator = agentInit("Crew/agents/validator_config.yaml")
    analyzer = agentInit("Crew/agents/analyzer_config.yaml")
    agents = [tutor, domain_expert, validator, analyzer]
    return crewConfig(agents=agents, tasks=[])