from a2a_cross_framework_poc.writer_agent_langgraph.agent_flow import create_writer_agent_graph
from langchain_core.messages import HumanMessage


if __name__ == "__main__":
    graph = create_writer_agent_graph()

    user_input = [
        HumanMessage(content="Write a short post on the importance of A2A protocol.")
    ]

    result = graph.invoke({"messages": user_input})
    final_message = result["messages"][-1]

    print("\n=== Writer Agent Response ===\n")
    print(final_message.content)
