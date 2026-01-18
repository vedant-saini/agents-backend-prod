from crewai import Agent

def create_manager(llm):
    return Agent(
        role="Manager",
        goal="Analyze project requirements and create an execution plan",
        backstory="Expert software project manager",
        allow_delegation=True,
        verbose=True,
        llm=llm
    )