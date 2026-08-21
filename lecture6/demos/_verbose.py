# _verbose.py
# Print each step of a create_agent run so beginners can see the loop.
#
# Same helper as Lecture 5, plus optional `config` for thread_id
# (needed once we add a checkpointer / store).

def run_verbose(agent, question: str, config: dict | None = None) -> str:
    """Run the agent and print every tool call + the final answer."""
    print(f"\n  Question: {question}")

    inputs = {"messages": [{"role": "user", "content": question}]}
    final_answer = None

    stream_args = (inputs,) if config is None else (inputs, config)

    for step in agent.stream(*stream_args, stream_mode="updates"):
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
