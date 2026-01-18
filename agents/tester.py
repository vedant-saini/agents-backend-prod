from crewai import Agent

def create_tester(llm):
    return Agent(
        role="Software Tester",
        goal="Detect bugs, fix code, and generate test cases",
        backstory="Detail-oriented tester obsessed with correctness",
        allow_delegation=False,
        verbose=True,
        llm=llm
    )