from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.tools import FunctionTool
from ad_genius_capstone.tools.ad_validator_tool import validate_ad_assets

# --- VALIDATOR AGENT CONFIGURATION ---
# Persona: Compliance Officer / QA.
# Goal: Enforce strict character limits and policy constraints using tools.

VALIDATOR_INSTRUCTION = """
You are 'The Compliance Officer'. Your job is to ensure Google Ads assets meet technical constraints.

### PROTOCOL
1.  Receive JSON input with `headlines` and `descriptions`.
2.  Call the tool `validate_ad_assets` with these lists.
3.  **Analyze the Tool Output:**
    -   If status is **"REJECTED"**: Return a response starting with "FIX_REQUEST:" followed by the specific feedback from the tool.
    -   If status is **"APPROVED"**: Return exactly: "FINAL_SUCCESS".
4.  Ensure compliance with Google Ads Editorial Policies (No CAPS, no '!', unique assets).
"""

def get_validator_agent(model_name="gemini-2.5-flash"):
    """
    Initializes the Validator Agent equipped with the validation tool.
    """
    return LlmAgent(
        name="validator_agent",
        model=Gemini(model=model_name),
        instruction=VALIDATOR_INSTRUCTION,
        tools=[FunctionTool(validate_ad_assets)],
    )
