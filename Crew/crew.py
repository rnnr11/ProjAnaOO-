from crewai import Agent, Task, Crew, Process
import yaml

# Agent
def agentConfig(role, goal, backstory):
    agent = Agent(role=role, goal=goal, backstory=backstory, verbose=True, allow_delegation=False)
    return agent

def agentInit(path):
    with open(path, "r") as f:
        dados = yaml.safe_load(f)
        agent = agentConfig(**dados)
    return agent

# Task

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