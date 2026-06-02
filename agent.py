# project4/agent.py
#
# The ReAct agent loop for Project 4.
# Receives a question about a dataset,
# decides which tools to use,
# and returns a final answer.

import os
from dotenv import load_dotenv
from anthropic import Anthropic
from tools import TOOLS, run_tool

load_dotenv()
client = Anthropic()


def run_agent(question: str, filepath: str, max_steps: int = 10) -> dict:
    """
    Runs the agent to answer a question about a dataset.

    Parameters:
    - question:  what the user wants to know
    - filepath:  path to the CSV file to analyse
    - max_steps: maximum tool calls before stopping

    Returns a dictionary with:
    - answer:     Claude's plain English explanation
    - steps:      how many steps were taken
    - charts:     list of chart paths generated
    """

    print(f"\nQuestion: {question}")
    print(f"Dataset:  {filepath}")
    print("-" * 50)

    # Track charts generated during this run
    charts_generated = []

    # System prompt — tells Claude what it is and how to behave
    system_prompt = f"""You are an expert data analyst assistant.

You have been given a CSV dataset at: {filepath}

Your job:
1. Always load the dataset first using load_dataset
2. Use the available tools to analyse the data
3. Answer the user's question with specific numbers and facts
4. Generate a chart when it would help visualise the answer
5. Give a clear plain English explanation at the end

Be specific — use actual numbers from the analysis.
Plain text only in your final answer. No markdown."""

    # Start conversation
    messages = [
        {"role": "user", "content": question}
    ]

    step = 0

    while step < max_steps:

        step += 1
        print(f"\nStep {step}:")

        # Call Claude
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            system=system_prompt,
            tools=TOOLS,
            messages=messages
        )

        print(f"  Decision: {response.stop_reason}")

        # ── Claude is done ──
        if response.stop_reason == "end_turn":
            final_answer = response.content[0].text
            print(f"\nFinal Answer: {final_answer}")

            return {
                "answer": final_answer,
                "steps": step,
                "charts": charts_generated
            }

        # ── Claude wants to use a tool ──
        if response.stop_reason == "tool_use":

            # Add Claude's response to history
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            tool_results = []

            for block in response.content:

                if block.type == "tool_use":

                    tool_name  = block.name
                    tool_input = block.input

                    print(f"  Tool: {tool_name}")
                    print(f"  Input: {tool_input}")

                    # Run the tool
                    try:
                        result = run_tool(tool_name, tool_input)
                        print(f"  Result: {result[:100]}...")  # show first 100 chars

                        # Track any charts generated
                        if tool_name == "generate_chart" and "saved to" in result:
                            chart_path = result.split("saved to ")[-1].strip()
                            charts_generated.append(chart_path)

                    except Exception as e:
                        result = f"Tool error: {e}"
                        print(f"  Error: {e}")

                    tool_results.append({
                        "type":        "tool_result",
                        "tool_use_id": block.id,
                        "content":     result
                    })

            # Add tool results to conversation
            messages.append({
                "role": "user",
                "content": tool_results
            })

    # Hit max steps
    return {
        "answer": "Could not complete analysis within step limit.",
        "steps": step,
        "charts": charts_generated
    }