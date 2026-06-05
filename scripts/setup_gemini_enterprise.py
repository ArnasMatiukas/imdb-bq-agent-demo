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
