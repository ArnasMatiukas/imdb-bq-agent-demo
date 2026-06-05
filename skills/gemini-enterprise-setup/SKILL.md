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
Run the interactive setup script using Python:
```bash
python3 scripts/setup_gemini_enterprise.py
```

#### Option B: Direct `gcloud` CLI Command
Execute the IAM policy binding manually in your terminal:
```bash
gcloud projects add-iam-policy-binding <PROJECT_ID> \
    --member="user:<CLIENT_EMAIL>" \
    --role="roles/aiplatform.user"
```

---

### Phase 3: Construct the A2A (Agent-to-Agent) Registration Card
Construct the exact A2A Card URL required by Gemini Enterprise using this structure:

```text
https://<LOCATION>-aiplatform.googleapis.com/v1beta1/projects/<PROJECT_ID>/locations/<LOCATION>/reasoningEngines/<REASONING_ENGINE_ID>/a2a
```

---

### Phase 4: Register in Workspace Admin Console
1. Log in to the Google Workspace Admin Console (`admin.google.com`) with administrator credentials.
2. Navigate to: **Apps > Google Workspace > Gemini > Extensions & Custom Agents**.
3. Click on **Add Custom Agent / Register New Extension**.
4. Paste the constructed **A2A Agent Card URL** and complete registration.
5. Grant or restrict access to specific organizational units (OUs) or Google Groups.
