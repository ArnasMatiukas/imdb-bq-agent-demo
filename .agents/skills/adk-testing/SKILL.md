---
name: adk-testing
description: >-
  Automates the complete local and remote verification loop for the IMDb BigQuery ADK agent.
  It reads the agent codebase, runs it locally, auto-heals any errors, deploys the agent, and
  verifies the live reasoning engine.
---

# ADK Testing & Auto-Healing System

## Overview
The **`adk-testing`** skill provides a standardized, automated workflow to test the IMDb ADK agent locally, deploy it, and verify its behavior in Google Cloud Agent Engine. It uses a dynamic, context-aware approach to verify queries, and executes an iterative self-healing/diagnostic loop to resolve errors (such as API mismatches, tool permission blocks, or syntax bugs).

---

## Workflow

### Phase 1: Dynamic Test Case Synthesis
1. Formulate a representative test query that triggers the agent's primary features:
   - *"What are the top 5 highest rated movies with at least 100000 votes in the imdb dataset?"*
2. Save this query to `tests/test_cases.json` inside the agent's folder so that it is persistent and reusable:
   ```json
   {
     "test_cases": [
       {
         "id": "tc_1",
         "description": "Verify highest rated movies retrieval",
         "query": "What are the top 5 highest rated movies with at least 100000 votes in the imdb dataset?"
       }
     ]
   }
   ```

---

### Phase 2: Local Test Execution & Auto-Healing
1. Create a local test script running `InMemoryRunner` with the synthetic queries. Example structure:
   ```python
   import sys
   import asyncio
   sys.path.insert(0, ".")
   from agent.agent import root_agent
   from google.adk.runners import InMemoryRunner
   from google.genai.types import Part, Content

   async def main():
       runner = InMemoryRunner(agent=root_agent, app_name="imdb_bq_agent")
       await runner.session_service.create_session(app_name="imdb_bq_agent", user_id="u", session_id="s")
       msg = Content(role="user", parts=[Part.from_text(text="What are the top 5 highest rated movies with at least 100000 votes in the imdb dataset?")])
       async for event in runner.run_async(user_id="u", session_id="s", new_message=msg):
           if hasattr(event, "content") and event.content:
               print("Content:", "".join(p.text or "" for p in event.content.parts if p.text))
   asyncio.run(main())
   ```
2. Execute the test using the active python interpreter.
3. **Local Auto-Healing Loop (Capped at 3 Retries)**:
   - If execution fails (e.g., returns tracebacks, API 404 errors, credential errors, or empty results):
     1. Analyze the exact traceback or logged error.
     2. Formulate a minimal, elegant fix to correct the codebase.
     3. Apply the fix and re-run.

---

### Phase 3: Agent Deployment
1. Once local tests are verified as passing, deploy the agent to Google Cloud Agent Engine:
   ```bash
   python3 scripts/deploy.py
   ```
2. Parse the deployment log to extract the **Agent ID** (Reasoning Engine Resource ID).

---

### Phase 4: Live/Remote Session Verification
1. Create a non-interactive remote session test to connect to the live deployed Reasoning Engine's session service:
   ```python
   import sys
   import asyncio
   from google.adk.runners import Runner, App
   from agent.agent import root_agent
   from google.adk.cli.utils.service_factory import (
       create_session_service_from_options,
       create_artifact_service_from_options,
   )
   from google.genai.types import Part, Content

   async def main():
       session_service_uri = "agentengine://projects/<PROJECT_ID>/locations/<REGION>/reasoningEngines/<AGENT_ID>"
       session_service = create_session_service_from_options(
           base_dir=".",
           session_service_uri=session_service_uri,
           app_name_to_dir={"imdb_bq_agent": "agent"},
           use_local_storage=False,
       )
       artifact_service = create_artifact_service_from_options(
           base_dir=".",
           artifact_service_uri=None,
           use_local_storage=False,
       )
       app = App(name="imdb_bq_agent", root_agent=root_agent)
       runner = Runner(app=app, artifact_service=artifact_service, session_service=session_service)
       
       session = await session_service.create_session(app_name="imdb_bq_agent", user_id="test_user")
       msg = Content(role="user", parts=[Part.from_text(text="What are the top 5 highest rated movies with at least 100000 votes?")])
       
       async for event in runner.run_async(user_id="test_user", session_id=session.id, new_message=msg):
           if hasattr(event, "content") and event.content:
               print("Remote Content:", "".join(p.text or "" for p in event.content.parts if p.text))
       await runner.close()

   asyncio.run(main())
   ```
2. Execute and confirm successful completion of the live query.
