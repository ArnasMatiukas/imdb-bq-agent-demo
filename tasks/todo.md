# Plan: Deploy, Verify and Expose IMDb BQ Agent V2

## Tasks

- [x] **Verify Deployed V2 Agent is Operational** <!-- id: 0 -->
  - [x] Write a verification script to query the V2 reasoning engine `7751240316472000512`. <!-- id: 1 -->
  - [x] Run the script and verify it correctly queries the IMDb dataset via BigQuery MCP. <!-- id: 2 -->
- [x] **Setup Gemini Enterprise Integration** <!-- id: 3 -->
  - [x] Run `scripts/setup_gemini_enterprise.py` to register/expose the agent and assign the appropriate `roles/aiplatform.user` permission to the user identity `admin@amatiukas.altostrat.com`. <!-- id: 4 -->
- [x] **Clean Up Configs & Restore Placeholders** <!-- id: 5 -->
  - [x] Revert `agent/config.py` to safe placeholder values to ensure no secrets or environment-specific values are committed. <!-- id: 6 -->
  - [x] Exclude or delete local secret-bearing files (like `.agent_engine_config.json`) to keep the repo generic. <!-- id: 7 -->

## Verification & Review
- **V2 Verification Status**: ✅ SUCCESS
- **Result Output**:
  ```
  [imdb_bq_agent]: Based on the IMDb public dataset, here are the top 5 highest-rated movies with at least 100,000 votes.
  1. The Shawshank Redemption (1994) - Rating: 9.3 (3,179,483 votes)
  2. The Godfather (1972) - Rating: 9.2 (2,220,803 votes)
  3. The Dark Knight (2008) - Rating: 9.1 (3,158,885 votes)
  4. The Lord of the Rings: The Return of the King (2003) - Rating: 9.0 (2,159,581 votes)
  5. Schindler's List (1993) - Rating: 9.0 (1,582,324 votes)
  ```
- **Gemini Enterprise Integration Endpoints**:
  - **Agent Platform Resource Path**: `https://europe-west4-aiplatform.googleapis.com/v1/projects/main-73893914/locations/europe-west4/reasoningEngines/7751240316472000512`
  - **A2A Agent Card URL**: `https://europe-west4-aiplatform.googleapis.com/v1beta1/projects/main-73893914/locations/europe-west4/reasoningEngines/7751240316472000512/a2a`
  - **User Identity Configured**: `admin@amatiukas.altostrat.com` (assigned `roles/aiplatform.user` role successfully)
  - **Programmatic Discovery Engine Registration**: Registered successfully as agent ID `8632113318901546786` under Discovery Engine App `gemini-enterprise_1775471274011`.


