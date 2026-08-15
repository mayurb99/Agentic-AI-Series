# _verbose.py
# Print each step of a create_agent run so beginners can see the loop.
#
# create_agent has no verbose=True flag (that was legacy AgentExecutor).
# Instead we stream the graph and print:
#   1. which tool the model chose (+ arguments)
#   2. what the tool returned
#   3. the final answer
#
# Under the hood the graph alternates:
#   "model" -> maybe ask for a tool
#   "tools" -> run the tool, send result back
# until the model answers with no more tool calls.


def run_verbose(agent, question: str) -> str:
    """Run the agent and print every tool call + the final answer."""
    print(f"\n  Question: {question}")

    inputs = {"messages": [{"role": "user", "content": question}]}
    final_answer = None

    for step in agent.stream(inputs, stream_mode="updates"):
        for _node_name, node_output in step.items():
            for msg in node_output.get("messages", []):
                tool_calls = getattr(msg, "tool_calls", None)
                msg_type = getattr(msg, "type", "")

                if tool_calls:
                    for tc in tool_calls:
                        print(f"  1) Tool chosen: {tc['name']}")
                        print(f"     Arguments:   {tc['args']}")
                elif msg_type == "tool":
                    content = str(getattr(msg, "content", ""))
                    print(f"  2) Tool result: {content[:200]}")
                elif msg_type == "ai" and getattr(msg, "content", None):
                    final_answer = msg.content

    print(f"\n  FINAL ANSWER: {final_answer}")
    return final_answer
