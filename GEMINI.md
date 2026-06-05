# Gemini Agent Instructions: IMDb BigQuery Demo Agent

You are assisting with the **IMDb BigQuery Demo Agent**, an autonomous agent designed using the Google Agent Development Kit (ADK) to query and analyze the public IMDb database on Google Cloud BigQuery.

---

## Architecture Overview
The agent is designed as a standalone **`LlmAgent`** using a custom Gemini client:
1. **`agent/agent.py`**: Entrypoint initializing the ADK `LlmAgent`, setting up the `CustomGemini` model, and loading registered MCP servers.
2. **`agent/config.py`**: Centralized environment lookups (`PROJECT_ID`, `LOCATION`, `MCP_SERVER_NAME`).
3. **`agent/prompt.py`**: Defines the system instructions and constraints, including BigQuery schema context.

---

## Agent Mandates & Best Practices

### 1. Model Configuration
- **Model Name**: The agent strictly uses `gemini-3.5-flash`.

### 2. Environment Configurations
The codebase is designed to be completely environment-agnostic. All key parameters are loaded from environment variables:
- `GOOGLE_CLOUD_PROJECT`: Target Google Cloud Billing/Execution Project.
- `GOOGLE_CLOUD_LOCATION`: Deployment region.
- `MCP_SERVER_NAME`: The specific registered Resource ID of the BigQuery MCP server (e.g., `agentregistry-xxxx-xxxx-xxxx-xxxxxxxxxxxx`).

### 3. BigQuery Execution Constraints
When writing SQL or calling tools:
- Standard query execution and metadata lookup tools (like `execute_sql_readonly`) must run inside the target local project billing context (`PROJECT_ID`).
- However, all SQL queries must reference the IMDb dataset tables using their fully-qualified names pointing to the public project: `bigquery-public-data.imdb.<table_name>` (e.g., `bigquery-public-data.imdb.title_basics`).

---

## Automated Testing & Deployment
The workspace contains a reusable ADK testing skill inside `skills/adk-testing`. You must utilize this skill when asked to test or verify changes locally or remotely.
- **Local Testing**: Run the agent using `adk run agent`.
- **Cloud Deployment**: Run the automated `scripts/deploy.py` using Python.
