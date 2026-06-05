---
name: gemini-enterprise-setup
description: >-
  Guides AI agents and developers on setting up secure access, configuring IAM roles,
  and registering a deployed Vertex AI Reasoning Engine as a custom extension in Gemini Enterprise.
---

# Gemini Enterprise Onboarding & Extension Integration Skill

## Overview
This skill provides a standardized workflow to configure project and resource permissions enabling Gemini Enterprise clients (Workspace users, groups, or service accounts) to invoke custom agents deployed via the Vertex AI Agent Engine.

---

## Onboarding & Integration Workflow

### Phase 1: Identity & Caller Resolution
1. Identify the email address or group representing the Gemini Enterprise client workspace. This is the caller identity making requests to your reasoning engine.
2. Verify that you have:
   - Target GCP `PROJECT_ID`
   - Deployment `REGION`
   - Active `REASONING_ENGINE_ID`

---

### Phase 2: Role Assignment (Vertex AI User)
To allow the enterprise client to invoke the agent's query and streaming APIs, grant the caller the **Vertex AI User** (`roles/aiplatform.user`) role at the project or resource level:

#### Option A: Using the Automated Script
Run the automated setup script using Python. You can run it interactively:
```bash
python3 scripts/setup_gemini_enterprise.py
```
Or specify all variables as command-line arguments (perfect for automated deployments) and execute a safe **dry-run** to verify setup:
```bash
python3 scripts/setup_gemini_enterprise.py \
    --project=<PROJECT_ID> \
    --region=<REGION> \
    --engine-id=<REASONING_ENGINE_ID> \
    --identity=<CLIENT_EMAIL> \
    --dry-run
```

#### Option B: Direct `gcloud` CLI Command
Execute the IAM policy binding manually in your terminal:
```bash
gcloud projects add-iam-policy-binding <PROJECT_ID> \
    --member="user:<CLIENT_EMAIL>" \
    --role="roles/aiplatform.user"
```

---

### Phase 3: Construct the Integration Resource Path or Card URL

You can integrate your agent with Gemini Enterprise using one of two pathways:

#### Pathway A: Native Agent Platform / ADK Integration (Recommended)
This uses the official ADK agent path to natively route messages via the Agent Platform.
* **Resource Path Format**:
  ```text
  https://<LOCATION>-aiplatform.googleapis.com/v1/projects/<PROJECT_ID>/locations/<LOCATION>/reasoningEngines/<REASONING_ENGINE_ID>
  ```

#### Pathway B: Standard A2A Card URL Integration
This routes queries via the Agent-to-Agent (A2A) protocol compatibility endpoint.
* **Card URL Format**:
  ```text
  https://<LOCATION>-aiplatform.googleapis.com/v1beta1/projects/<PROJECT_ID>/locations/<LOCATION>/reasoningEngines/<REASONING_ENGINE_ID>/a2a
  ```

---

### Phase 4: Register in Google Cloud / Workspace Console
1. Log in to the Google Cloud Console and navigate to **Gemini Enterprise > Apps**.
2. Click on your active App name, navigate to **Agents**, and select **Add Agent**.
3. Choose the integration style:
   - For **Pathway A (Recommended)**: Select **Custom agent via Agent Platform** and paste the **Agent Platform Resource Path** constructed above.
   - For **Pathway B**: Select **Custom agent via A2A** and paste the **A2A Agent Card URL** constructed above.
4. If registering programmatically via the `discoveryengine` REST API, send a POST request with the `adkAgentDefinition.provisionedReasoningEngine.reasoningEngine` field pointing to `projects/<PROJECT_ID>/locations/<LOCATION>/reasoningEngines/<REASONING_ENGINE_ID>`.
5. Share the registered agent with users, OUs, or Google Groups to enable querying via `@imdb_bq_agent` or your configured agent name!
