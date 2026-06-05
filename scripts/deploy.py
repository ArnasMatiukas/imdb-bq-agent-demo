import os
import sys
import subprocess
import time
import shutil
from typing import Optional

# Ensure we're running from the project root
if os.getcwd().endswith('scripts'):
    os.chdir('..')

# Environment variables needed for deployment (override via env vars)
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "<YOUR_PROJECT_ID>")
REGION = os.environ.get("GOOGLE_CLOUD_LOCATION", "<YOUR_REGION>")
SA_NAME = "imdb-bq-agent-sa"
SA_EMAIL = f"{SA_NAME}@{PROJECT_ID}.iam.gserviceaccount.com"
DISPLAY_NAME = "IMDb BQ Agent"

os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"] = REGION

def run_command(command: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Runs a shell command and captures output."""
    print(f"Running: {' '.join(command)}")
    return subprocess.run(command, check=check, text=True, capture_output=True)

def setup_service_account():
    if "<YOUR_PROJECT_ID>" in PROJECT_ID:
        print("Error: Please set GOOGLE_CLOUD_PROJECT environment variable.")
        sys.exit(1)
        
    print(f"\n--- Ensuring dedicated Service Account exists: {SA_EMAIL} ---")
    
    # Check if SA exists
    result = run_command(["gcloud", "iam", "service-accounts", "describe", SA_EMAIL, f"--project={PROJECT_ID}"], check=False)
    
    if result.returncode != 0:
        print("Creating service account...")
        run_command([
            "gcloud", "iam", "service-accounts", "create", SA_NAME,
            f"--display-name=IMDb BQ Agent Runtime SA",
            f"--project={PROJECT_ID}"
        ])
    else:
        print("Service account already exists.")

    print("\n--- Assigning necessary IAM roles ---")
    roles = [
        "roles/aiplatform.user",
        "roles/agentregistry.viewer",
        "roles/bigquery.dataViewer",
        "roles/bigquery.jobUser",
        "roles/bigquery.user",
        "roles/serviceusage.serviceUsageConsumer",
        "roles/telemetry.admin"
    ]
    
    for role in roles:
        print(f"Assigning {role}...")
        run_command([
            "gcloud", "projects", "add-iam-policy-binding", PROJECT_ID,
            f"--member=serviceAccount:{SA_EMAIL}",
            f"--role={role}"
        ])
        
    print("Roles assigned successfully. Waiting 5 seconds for IAM propagation...")
    time.sleep(5)

def get_existing_agent_id() -> Optional[str]:
    if "<YOUR_PROJECT_ID>" in PROJECT_ID or "<YOUR_REGION>" in REGION:
        return None
        
    print(f"\n--- Checking for existing Agent Engine instance: '{DISPLAY_NAME}' ---")
    
    try:
        import vertexai
        from vertexai.preview import reasoning_engines
        
        vertexai.init(project=PROJECT_ID, location=REGION)
        engines = reasoning_engines.ReasoningEngine.list()
        for e in engines:
            if e.display_name == DISPLAY_NAME:
                agent_id = e.resource_name.split("/")[-1]
                print(f"Found existing agent with ID: {agent_id}")
                return agent_id
    except Exception as e:
        print(f"Could not list engines (this is expected if it's the first run): {e}")
            
    print("No existing agent found.")
    return None

def deploy_agent(existing_agent_id: Optional[str]):
    print(f"\n--- Starting ADK deployment using service account: {SA_EMAIL} ---")
    
    adk_path = shutil.which("adk")
    if not adk_path:
        print("Error: 'adk' command not found in your environment PATH.")
        print("Please activate your virtual environment where google-adk is installed.")
        sys.exit(1)

    command = [
        adk_path, "deploy", "agent_engine",
        f"--project={PROJECT_ID}",
        f"--region={REGION}",
        f"--display_name={DISPLAY_NAME}",
        "--requirements_file=requirements.txt",
        "--skip-agent-import-validation",
        "--otel_to_cloud",
        "--trace_to_cloud"
    ]
    
    if existing_agent_id:
        command.append(f"--agent_engine_id={existing_agent_id}")
        
    # the target agent directory
    command.append("agent")
    
    print(f"Running: {' '.join(command)}")
    subprocess.run(command, check=True)

def print_a2a_url():
    agent_id = get_existing_agent_id()
    
    if agent_id:
        a2a_url = f"https://{REGION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{agent_id}/a2a"
        print("\n============================================================")
        print("✅ Agent Engine Deployment Successful!")
        print(f"Agent ID: {agent_id}")
        print("\n🔗 A2A Agent Card URL (for Gemini CLI integration):")
        print(a2a_url)
        print("============================================================")
    else:
        print("\nWarning: Could not determine final Agent Engine ID to print the A2A URL.")

if __name__ == "__main__":
    try:
        setup_service_account()
        existing_id = get_existing_agent_id()
        deploy_agent(existing_id)
        print_a2a_url()
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Deployment failed during command execution.")
        if e.stderr:
            print(f"Error output:\n{e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        sys.exit(1)
