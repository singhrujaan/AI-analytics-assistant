# project4/test_tools.py
# Test every tool works correctly before building the agent

import sys
sys.path.append('project4')  # so we can import tools.py

from tools import load_dataset, get_statistics, run_analysis, generate_chart

print("=" * 50)
print("TEST 1 — Load Dataset")
print("=" * 50)
result = load_dataset("project/data/sales_data.csv")
print(result)

print("\n" + "=" * 50)
print("TEST 2 — Get Statistics (whole dataset)")
print("=" * 50)
result = get_statistics()
print(result)

print("\n" + "=" * 50)
print("TEST 3 — Get Statistics (one column)")
print("=" * 50)
result = get_statistics("sales")
print(result)

print("\n" + "=" * 50)
print("TEST 4 — Run Analysis")
print("=" * 50)
result = run_analysis("what are the top values")
print(result)

print("\n" + "=" * 50)
print("TEST 5 — Generate Chart")
print("=" * 50)
result = generate_chart("bar", "product", "sales", "Sales by Product")
print(result)

print("\nAll tools tested.")