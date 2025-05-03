# src/a2a_cross_framework_poc/editor_agent_crewai/main.py

from dotenv import load_dotenv
load_dotenv()

from crewai import Task, Crew
from a2a_cross_framework_poc.editor_agent_crewai.agent_config import get_translator_agent

# 1. Instantiate your agent
translator = get_translator_agent()

# 2. The text you want translated
english_text = (
    "The A2A protocol enables agents across different frameworks "
    "to talk, collaborate, and complete tasks together. "
    "It is designed for secure, structured, and modality-agnostic agent communication."
)

# 3. Create a Task — note the required `expected_output` field
translation_task = Task(
    description=f"Translate the following text to Chinese:\n\n{english_text}",
    agent=translator,
    expected_output="",  # placeholder string satisfies the Pydantic requirement
)

# 4. Create and run the Crew
crew = Crew(
    agents=[translator],
    tasks=[translation_task],
    verbose=True
)

# 5. Execute and capture the result
results = crew.kickoff()

# Depending on CrewAI’s return format, it might return a dict of {Task: output} or a simple string
if isinstance(results, dict):
    # get the output for our single task
    translated_output = next(iter(results.values()))
else:
    translated_output = results

print("\n=== Translated Output ===\n")
print(translated_output)
