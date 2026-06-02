### Project 4 — AI Analytics Assistant 
- FastAPI backend with file upload and question endpoints
- ReAct agent autonomously decides which tools to use
- Tools: load dataset, run analysis, get statistics, generate charts
- Claude explains findings in plain English
- Returns structured JSON with answer + chart paths
- **Stack:** FastAPI, Anthropic Claude, pandas, matplotlib, Pydantic
- **Run:** uvicorn app:app --reload --port 8000
