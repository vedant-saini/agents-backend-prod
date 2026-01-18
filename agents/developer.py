from crewai import Agent

def create_developer(llm):
    return Agent(
        role="Software Developer",
        goal="Write clean, optimized, and error-free code",
        backstory="Senior developer with strong problem-solving skills",
        allow_delegation=False,
        verbose=True,
        llm=llm
    )