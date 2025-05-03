# src/a2a_cross_framework_poc/editor_agent_crewai/agent_config.py

from crewai import Agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

def get_translator_agent():
    return Agent(
        role="Translator",
        goal="Translate English text to Chinese",
        backstory="You are an expert translator fluent in English and Chinese, known for your accurate and culturally-sensitive translations.",
        llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    )
