import os
import sys
import subprocess

def run_command(command: list[str]) -> subprocess.CompletedProcess:
    """Runs a shell command and captures output."""
    print(f"Running: {' '.join(command)}")
    return subprocess.run(command, check=True, text=True, capture_output=True)

def setup_integration():
    print("============================================================")
    print("💼 Gemini Enterprise & Workspace Extension Setup")
    print("============================================================")
    
    # 1. Retrieve configurations from environment or prompt
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        project_id = input("Enter your GCP Project ID: ").strip()
        
    region = os.environ.get("GOOGLE_CLOUD_LOCATION")
    if not region:
        region = input("Enter your Deployment Region (e.g., europe-west4, us-central1): ").strip()
        
    reasoning_engine_id = input("Enter your Deployed Reasoning Engine ID: ").strip()
    
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
        
    # 3. Formulate and print A2A Card URL
    a2a_url = f"https://{region}-aiplatform.googleapis.com/v1beta1/projects/{project_id}/locations/{region}/reasoningEngines/{reasoning_engine_id}/a2a"
    
    print("\n============================================================")
    print("🎉 Integration Setup Complete!")
    print("============================================================")
    print(f"🔗 **A2A Agent Card URL** for Gemini Enterprise:")
    print(a2a_url)
    print("\n👉 **Next Steps**:")
    print("1. Copy the A2A Agent Card URL above.")
    print("2. Open your Google Workspace Admin Console (Gemini Enterprise panel).")
    print("3. Navigate to **Apps > Gemini > Extensions & Custom Agents**.")
    print("4. Click **Add Custom Agent**, paste the A2A URL, and click Register.")
    print("5. Your users will now be able to query this agent in Workspace using `@imdb_bq_agent`!")
    print("============================================================")

if __name__ == "__main__":
    try:
        setup_integration()
    except KeyboardInterrupt:
        print("\nSetup cancelled.")
        sys.exit(0)
