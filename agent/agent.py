import os
from functools import cached_property
from google.adk.agents import LlmAgent
from google.adk.integrations.agent_registry import AgentRegistry
from google.adk.models import Gemini
from google.genai import Client

from .config import (
    AGENT_NAME,
    AGENT_DESCRIPTION,
    PROJECT_ID,
    LOCATION,
    MCP_SERVER_NAME,
)
from .prompt import INSTRUCTION

class CustomGemini(Gemini):
    @cached_property
    def api_client(self) -> Client:
        return Client(
            vertexai=True,
            project=PROJECT_ID,
            location="global",
        )

def create_agent() -> LlmAgent:
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
    
    registry = AgentRegistry(project_id=PROJECT_ID, location=LOCATION)
    
    analytics_mcp = registry.get_mcp_toolset(
        f"projects/{PROJECT_ID}/locations/global/mcpServers/{MCP_SERVER_NAME}"
    )
    analytics_mcp.tool_filter = ["get_dataset_info", "list_table_ids", "get_table_info", "execute_sql_readonly"]

    return LlmAgent(
        name=AGENT_NAME,
        model=CustomGemini(model="gemini-3.5-flash"),
        description=AGENT_DESCRIPTION,
        instruction=INSTRUCTION,
        tools=[analytics_mcp]
    )

root_agent = create_agent()
