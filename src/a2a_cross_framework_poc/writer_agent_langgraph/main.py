# src/a2a_cross_framework_poc/writer_agent_langgraph/main.py

from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

from a2a_cross_framework_poc.writer_agent_langgraph.agent_flow import create_writer_agent_graph

load_dotenv()

if __name__ == "__main__":
    # CLI testing only — this does not run in A2A server
    topic = input("Enter blog topic: ")
    graph = create_writer_agent_graph()
    initial_state = {"messages": [HumanMessage(content=topic)]}
    state = graph.invoke(initial_state)

    blog_output = state["messages"][-1].content.strip()
    print("\n=== Written Blog ===\n")
    print(blog_output)
