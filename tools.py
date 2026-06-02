# project4/tools.py
#
# All the tools the agent can use.
# Each function does one specific thing.
# The agent decides which ones to call and when.

import os
import json
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # prevents matplotlib from trying to open a window
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
import numpy as np

# ── Global state ──
# Stores the currently loaded dataset
# so all tools can access it
current_df = None
current_filename = ""


# ════════════════════════════════════
# TOOL 1 — Load Dataset
# ════════════════════════════════════


def load_dataset(filepath: str) -> str:
    """
    Loads a CSV file into pandas.
    Stores it globally so other tools can use it.
    Returns a summary of what was loaded.
    """
    global current_df, current_filename

    try:
        # Load the CSV file
        current_df = pd.read_csv(filepath)
        current_filename = os.path.basename(filepath)

        # Build a summary to return to the agent
        summary = f"""
Dataset loaded: {current_filename}
Rows: {len(current_df)}
Columns: {len(current_df.columns)}
Column names: {list(current_df.columns)}
Missing values: {current_df.isnull().sum().sum()} total
        """.strip()

        return summary

    except Exception as e:
        return f"Error loading dataset: {e}"


# ════════════════════════════════════
# TOOL 2 — Get Statistics
# ════════════════════════════════════


def get_statistics(column: str = None) -> str:
    """
    Returns statistics about the dataset.
    If column is provided — stats for that column only.
    If no column — overview of the whole dataset.
    """
    global current_df

    # Check dataset is loaded
    if current_df is None:
        return "No dataset loaded. Please load a dataset first."

    try:
        if column:
            # Stats for one specific column
            if column not in current_df.columns:
                return f"Column '{column}' not found. Available: {list(current_df.columns)}"

            col_data = current_df[column]

            # Numeric column
            if col_data.dtype in ["int64", "float64"]:
                stats = {
                    "column": column,
                    "type": "numeric",
                    "mean": round(float(col_data.mean()), 2),
                    "median": round(float(col_data.median()), 2),
                    "std": round(float(col_data.std()), 2),
                    "min": round(float(col_data.min()), 2),
                    "max": round(float(col_data.max()), 2),
                    "missing": int(col_data.isnull().sum()),
                }
            else:
                # Categorical column
                stats = {
                    "column": column,
                    "type": "categorical",
                    "unique_values": int(col_data.nunique()),
                    "most_common": str(col_data.mode()[0]),
                    "value_counts": col_data.value_counts().head(5).to_dict(),
                    "missing": int(col_data.isnull().sum()),
                }

            return json.dumps(stats, indent=2)

        else:
            # Overview of whole dataset
            overview = {
                "rows": len(current_df),
                "columns": len(current_df.columns),
                "column_names": list(current_df.columns),
                "numeric_columns": list(
                    current_df.select_dtypes(include="number").columns
                ),
                "text_columns": list(
                    current_df.select_dtypes(include="object").columns
                ),
                "missing_values": current_df.isnull().sum().to_dict(),
            }
            return json.dumps(overview, indent=2)

    except Exception as e:
        return f"Error getting statistics: {e}"


# ════════════════════════════════════
# TOOL 3 — Run Analysis
# ════════════════════════════════════


def run_analysis(question: str) -> str:
    """
    Runs a pandas analysis based on a plain English question.
    Handles common analysis patterns automatically.
    """
    global current_df

    if current_df is None:
        return "No dataset loaded. Please load a dataset first."

    try:
        question_lower = question.lower()

        # ── Pattern 1: Top N values ──
        if (
            "top" in question_lower
            or "highest" in question_lower
            or "most" in question_lower
        ):
            # Find numeric columns to rank by
            numeric_cols = current_df.select_dtypes(include="number").columns.tolist()
            if numeric_cols:
                top_col = numeric_cols[0]
                result = current_df.nlargest(5, top_col)[
                    [top_col]
                    + list(current_df.select_dtypes(include="object").columns[:2])
                ]
                return f"Top 5 by {top_col}:\n{result.to_string()}"

        # ── Pattern 2: Average / mean ──
        elif "average" in question_lower or "mean" in question_lower:
            numeric_cols = current_df.select_dtypes(include="number").columns
            averages = current_df[numeric_cols].mean().round(2)
            return f"Averages:\n{averages.to_string()}"

        # ── Pattern 3: Count / how many ──
        elif "count" in question_lower or "how many" in question_lower:
            return f"Total rows: {len(current_df)}\nValue counts per column:\n{current_df.count().to_string()}"

        # ── Pattern 4: Correlation ──
        elif "correlat" in question_lower or "relationship" in question_lower:
            numeric_cols = current_df.select_dtypes(include="number")
            if len(numeric_cols.columns) >= 2:
                corr = numeric_cols.corr().round(3)
                return f"Correlation matrix:\n{corr.to_string()}"
            return "Not enough numeric columns for correlation analysis"

        # ── Pattern 5: Missing values ──
        elif (
            "missing" in question_lower
            or "null" in question_lower
            or "empty" in question_lower
        ):
            missing = current_df.isnull().sum()
            missing_pct = (missing / len(current_df) * 100).round(1)
            result = pd.DataFrame(
                {"missing_count": missing, "missing_pct": missing_pct}
            )
            return f"Missing values:\n{result.to_string()}"

        # ── Default: general summary ──
        else:
            return f"Dataset summary:\n{current_df.describe().round(2).to_string()}"

    except Exception as e:
        return f"Analysis error: {e}"


# ════════════════════════════════════
# TOOL 4 — Generate Chart
# ════════════════════════════════════


def generate_chart(
    chart_type: str, x_column: str, y_column: str = None, title: str = ""
) -> str:
    """
    Generates a chart and saves it as a PNG file.
    Returns the file path so the API can serve it.

    chart_type options: bar, line, histogram, scatter
    """
    global current_df

    if current_df is None:
        return "No dataset loaded. Please load a dataset first."

    try:
        # Create the chart directory if it doesn't exist
        os.makedirs("project/charts", exist_ok=True)

        # Create a new figure
        plt.figure(figsize=(10, 6))

        if chart_type == "bar":
            if y_column and y_column in current_df.columns:
                data = (
                    current_df.groupby(x_column)[y_column]
                    .mean()
                    .sort_values(ascending=False)
                    .head(10)
                )
                data.plot(kind="bar", color="#4f8ef7")
                plt.ylabel(y_column)
            else:
                current_df[x_column].value_counts().head(10).plot(
                    kind="bar", color="#4f8ef7"
                )
                plt.ylabel("Count")

        elif chart_type == "line":
            if y_column and y_column in current_df.columns:
                plt.plot(current_df[x_column], current_df[y_column], color="#38d9a9")
                plt.ylabel(y_column)
            else:
                current_df[x_column].plot(kind="line", color="#38d9a9")

        elif chart_type == "histogram":
            current_df[x_column].dropna().plot(
                kind="hist", bins=20, color="#f7c948", edgecolor="white"
            )
            plt.ylabel("Frequency")

        elif chart_type == "scatter":
            if y_column and y_column in current_df.columns:
                plt.scatter(
                    current_df[x_column],
                    current_df[y_column],
                    alpha=0.5,
                    color="#bc8cff",
                )
                plt.ylabel(y_column)

        # Labels and title
        plt.title(title or f"{chart_type.title()} Chart — {x_column}")
        plt.xlabel(x_column)
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save the chart
        chart_path = f"project/charts/{chart_type}_{x_column}.png"
        plt.savefig(chart_path, dpi=150, bbox_inches="tight")
        plt.close()

        return f"Chart saved to {chart_path}"

    except Exception as e:
        plt.close()
        return f"Chart error: {e}"


# ════════════════════════════════════
# TOOL DEFINITIONS FOR THE AGENT
# ════════════════════════════════════
# These descriptions are what Claude reads
# to decide which tool to use

TOOLS = [
    {
        "name": "load_dataset",
        "description": "Loads a CSV dataset from a file path. Always call this first before any analysis.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "The full file path to the CSV file",
                }
            },
            "required": ["filepath"],
        },
    },
    {
        "name": "get_statistics",
        "description": "Gets statistics about the dataset. Pass a column name for specific column stats, or leave empty for overall dataset overview.",
        "input_schema": {
            "type": "object",
            "properties": {
                "column": {
                    "type": "string",
                    "description": "Optional. The column name to get statistics for.",
                }
            },
        },
    },
    {
        "name": "run_analysis",
        "description": "Runs analysis on the dataset based on a question. Handles top values, averages, counts, correlations, and missing values.",
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The analysis question to answer. Example: what are the top values, what is the average, how many rows",
                }
            },
            "required": ["question"],
        },
    },
    {
        "name": "generate_chart",
        "description": "Generates and saves a chart as a PNG file. Use this when the user asks for a visualization or chart.",
        "input_schema": {
            "type": "object",
            "properties": {
                "chart_type": {
                    "type": "string",
                    "description": "Type of chart: bar, line, histogram, or scatter",
                },
                "x_column": {
                    "type": "string",
                    "description": "The column to use for the x axis",
                },
                "y_column": {
                    "type": "string",
                    "description": "Optional. The column to use for the y axis.",
                },
                "title": {
                    "type": "string",
                    "description": "Optional. The chart title.",
                },
            },
            "required": ["chart_type", "x_column"],
        },
    },
]


# ════════════════════════════════════
# TOOL ROUTER
# ════════════════════════════════════


def run_tool(tool_name: str, tool_input: dict) -> str:
    """
    Routes tool calls from the agent to the right function.
    """
    if tool_name == "load_dataset":
        return load_dataset(tool_input["filepath"])
    elif tool_name == "get_statistics":
        return get_statistics(tool_input.get("column"))
    elif tool_name == "run_analysis":
        return run_analysis(tool_input["question"])
    elif tool_name == "generate_chart":
        return generate_chart(
            tool_input["chart_type"],
            tool_input["x_column"],
            tool_input.get("y_column"),
            tool_input.get("title", ""),
        )
    else:
        return f"Unknown tool: {tool_name}"
