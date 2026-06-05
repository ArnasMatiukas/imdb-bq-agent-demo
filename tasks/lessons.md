# SRE & Agent Deployment Lessons Learned

## Verification & Deployment Patterns

- **Reasoning Engine IAM Constraints**:
  - Vertex AI Reasoning Engines execute under the Vertex AI Custom Code Service Agent identity by default.
  - When querying custom MCP servers (like BigQuery), these default identities lack access (`403 Forbidden`).
  - **Resolution**: Use `.agent_engine_config.json` inside the agent folder to override the execution identity with a custom service account that has appropriate viewer and toolUser access.

- **Gemini Enterprise Automatic Integration & Discovery**:
  - Simply assigning `roles/aiplatform.user` does not automatically surface the agent in Gemini Enterprise; it only authorizes access. The agent must be explicitly linked/registered under the project's Discovery Engine active engine.
  - **Resolution**: Integrate automatic engine discovery and programmatic registration directly inside the SRE setup script (`scripts/setup_gemini_enterprise.py`). The script should auto-discover existing Gemini Enterprise/Discovery Engine apps and programmatically invoke the `collections/default_collection/engines/.../assistants/default_assistant/agents` creation REST endpoint, avoiding manual user copy-pasting mistakes entirely.

