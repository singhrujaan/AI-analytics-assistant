# project4/test_agent.py
# Test the agent works before adding the API

import sys
sys.path.append('project')

from agent import run_agent

# Test 1 — Simple question
print("=" * 55)
print("TEST 1 — Simple analysis question")
print("=" * 55)
result = run_agent(
    question="What are types of products?",
    filepath="project/data/sales_data.csv"
)
print(f"\nAnswer: {result['answer']}")
print(f"Steps taken: {result['steps']}")
print(f"Charts: {result['charts']}")

# Test 2 — Chart generation
print("\n" + "=" * 55)
print("TEST 2 — Question that needs a chart")
print("=" * 55)
result = run_agent(
    question="Show me a scatter plot to compare different types of product sales.",
    filepath="project/data/sales_data.csv"
)
print(f"\nAnswer: {result['answer']}")
print(f"Steps taken: {result['steps']}")
print(f"Charts: {result['charts']}")