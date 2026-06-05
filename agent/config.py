import os

# Agent Metadata
AGENT_NAME = "imdb_bq_agent"
AGENT_DESCRIPTION = "Specialized Data Analyst for the IMDb public dataset. Analyzes BigQuery datasets for movies, actors, ratings, and reviews."

# Centralized Environment Configurations & Fallback Placeholders
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "<YOUR_PROJECT_ID>")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")
MCP_SERVER_NAME = os.environ.get("MCP_SERVER_NAME", "<YOUR_MCP_SERVER_NAME>")
