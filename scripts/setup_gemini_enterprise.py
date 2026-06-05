import os
import sys
import subprocess
import argparse

def run_command(command: list[str]) -> subprocess.CompletedProcess:
    """Runs a shell command and captures output."""
    print(f"Running: {' '.join(command)}")
    return subprocess.run(command, check=True, text=True, capture_output=True)

def setup_integration():
    print("============================================================")
    print("💼 Gemini Enterprise & Workspace Extension Setup")
    print("============================================================")
    
    parser = argparse.ArgumentParser(description="Configure Gemini Enterprise integration for Vertex AI Reasoning Engine.")
    parser.add_argument("--project", help="GCP Project ID")
    parser.add_argument("--region", help="GCP Region (e.g. europe-west4, us-central1)")
    parser.add_argument("--engine-id", help="Deployed Reasoning Engine ID")
    parser.add_argument("--identity", help="Gemini Enterprise calling identity email")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without modifying IAM policies")
    
    args = parser.parse_args()
    
    # 1. Retrieve configurations from arguments, environment or prompt
    project_id = args.project or os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        project_id = input("Enter your GCP Project ID: ").strip()
        
    region = args.region or os.environ.get("GOOGLE_CLOUD_LOCATION")
    if not region:
        region = input("Enter your Deployment Region (e.g., europe-west4, us-central1): ").strip()
        
    reasoning_engine_id = args.engine_id
    if not reasoning_engine_id:
        reasoning_engine_id = input("Enter your Deployed Reasoning Engine ID: ").strip()
    
    identity = args.identity
    if not identity:
        print("\nTo integrate with Gemini Enterprise, you must grant the calling identity")
        print("(User email, Google Group, or Service Account) the Vertex AI User role.")
        identity = input("Enter the Gemini Enterprise user/identity email (e.g. user@yourdomain.com): ").strip()
    
    if not identity:
        print("Error: Calling identity is required.")
        sys.exit(1)
        
    # Determine member prefix
    member = f"user:{identity}"
    if identity.endswith(".gserviceaccount.com"):
        member = f"serviceAccount:{identity}"
    elif "@googlegroups.com" in identity:
        member = f"group:{identity}"
    elif "domain:" in identity:
        member = identity # Already prefixed e.g. domain:yourdomain.com
        
    # 2. Grant IAM policy binding
    print(f"\n--- Assigning roles/aiplatform.user to {member} ---")
    if args.dry_run:
        print(f"[DRY-RUN] Would run: gcloud projects add-iam-policy-binding {project_id} --member={member} --role=roles/aiplatform.user")
    else:
        try:
            run_command([
                "gcloud", "projects", "add-iam-policy-binding", project_id,
                f"--member={member}",
                "--role=roles/aiplatform.user"
            ])
            print("✅ IAM policy binding added successfully.")
        except Exception as e:
            print(f"❌ Failed to bind IAM policy: {e}")
            print("Please ensure you have project administrator permissions to run this script.")
            sys.exit(1)
        
    # 3. Formulate URLs and Payloads
    adk_resource_path = f"https://{region}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{region}/reasoningEngines/{reasoning_engine_id}"
    a2a_url = f"https://{region}-aiplatform.googleapis.com/v1beta1/projects/{project_id}/locations/{region}/reasoningEngines/{reasoning_engine_id}/a2a"
    provisioned_path = f"projects/{project_id}/locations/{region}/reasoningEngines/{reasoning_engine_id}"

    # 4. Attempt automatic registration in Gemini Enterprise
    print("\n--- Attempting Programmatic Registration with Gemini Enterprise (Discovery Engine) ---")
    try:
        token_res = run_command(["gcloud", "auth", "print-access-token"])
        token = token_res.stdout.strip()
        
        import urllib.request
        import urllib.error
        import json
        
        # Fetch the list of existing engines
        url = f"https://global-discoveryengine.googleapis.com/v1alpha/projects/{project_id}/locations/global/collections/default_collection/engines"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {token}",
            "X-Goog-User-Project": project_id,
            "Content-Type": "application/json"
        }, method="GET")
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            
        engines = data.get("engines", [])
        if not engines:
            print("ℹ️ No active Gemini Enterprise / Discovery Engine apps found in this project.")
        else:
            # Look for gemini-enterprise engine first, or fallback to the first generic engine
            target_engine = None
            for eng in engines:
                if "gemini-enterprise" in eng.get("name", ""):
                    target_engine = eng
                    break
            if not target_engine:
                target_engine = engines[0]
                
            engine_name = target_engine.get("name")
            engine_id = engine_name.split("/")[-1]
            display_name = target_engine.get("displayName")
            
            print(f"🎯 Found active Gemini Enterprise App: '{display_name}' ({engine_id})")
            
            # Perform registration under the discovered engine
            reg_url = f"https://global-discoveryengine.googleapis.com/v1alpha/{engine_name}/assistants/default_assistant/agents"
            
            payload = {
                "displayName": "IMDb Analytics Agent V2",
                "description": "Specialized Data Analyst for the IMDb public dataset (V2). Analyzes BigQuery datasets for movies, actors, ratings, and reviews.",
                "adkAgentDefinition": {
                    "provisionedReasoningEngine": {
                        "reasoningEngine": f"projects/{project_id}/locations/{region}/reasoningEngines/{reasoning_engine_id}"
                    }
                },
                "sharingConfig": {
                    "scope": "ALL_USERS"
                }
            }
            
            reg_req = urllib.request.Request(reg_url, headers={
                "Authorization": f"Bearer {token}",
                "X-Goog-User-Project": project_id,
                "Content-Type": "application/json"
            }, data=json.dumps(payload).encode("utf-8"), method="POST")
            
            try:
                with urllib.request.urlopen(reg_req) as reg_response:
                    reg_data = json.loads(reg_response.read().decode("utf-8"))
                agent_resource_name = reg_data.get("name")
                print(f"✅ Successfully registered agent programmatically: {agent_resource_name}")
                print("🎉 The agent is now fully visible and active in your Gemini Enterprise interface!")
            except urllib.error.HTTPError as he:
                err_body = he.read().decode("utf-8")
                if he.code == 409:
                    print("ℹ️ Agent is already registered in this Gemini Enterprise app.")
                else:
                    print(f"⚠️ Registration attempt returned status {he.code}: {err_body}")
    except Exception as e:
        print(f"ℹ️ Optional automatic registration was skipped: {e}")

    print("\n============================================================")
    print("🎉 Integration Setup Complete!")
    print("============================================================")

    
    print("\n👉 Option 1: Native Agent Platform / ADK Integration (Recommended)")
    print("------------------------------------------------------------")
    print(f"🔗 **Agent Platform Resource Path**:")
    print(f"   {adk_resource_path}")
    print("\n📝 **Console Setup Steps**:")
    print("1. Open the Google Cloud Console and navigate to **Gemini Enterprise > Apps**.")
    print("2. Select your App, click on **Agents**, and then click **Add Agent**.")
    print("3. Click **Add** under **Custom agent via Agent Platform**.")
    print("4. Configure OAuth details (if required) and click **Next**.")
    print("5. Enter your desired display name and description.")
    print(f"6. Paste the **Agent Platform Resource Path** above into the resource field.")
    print("7. Click **Create**.")

    print("\n👉 Option 2: Custom Agent via A2A Protocol")
    print("------------------------------------------------------------")
    print(f"🔗 **A2A Agent Card URL**:")
    print(f"   {a2a_url}")
    print("\n📝 **Console Setup Steps**:")
    print("1. In Gemini Enterprise, click **Add Agent**.")
    print("2. Click **Add** under **Custom agent via A2A**.")
    print("3. Paste the **A2A Agent Card URL** above in the JSON field / URL input.")
    print("4. Complete the wizard.")

    print("\n💻 Option 3: Register via REST API (Discovery Engine)")
    print("------------------------------------------------------------")
    print("Run the following API request to register this ADK Agent programmatically:")
    print(f"""
curl -X POST \\
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \\
  -H "Content-Type: application/json" \\
  -H "X-Goog-User-Project: {project_id}" \\
  "https://global-discoveryengine.googleapis.com/v1alpha/projects/{project_id}/locations/global/collections/default_collection/engines/YOUR_APP_ID/assistants/default_assistant/agents" \\
  -d '{{
    "displayName": "IMDb BQ Agent",
    "description": "An autonomous agent that queries movie datasets using BigQuery.",
    "adkAgentDefinition": {{
      "provisionedReasoningEngine": {{
        "reasoningEngine": "{provisioned_path}"
      }}
    }}
  }}'
""")
    print("============================================================")

if __name__ == "__main__":
    try:
        setup_integration()
    except KeyboardInterrupt:
        print("\nSetup cancelled.")
        sys.exit(0)
