import os
import json
import re
import uuid
import logging
import asyncio
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

# --- GOOGLE ADK IMPORTS ---
from google.adk.models import Gemini
from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# --- CLOUD IMPORTS ---
from google.cloud import aiplatform

try:
    import vertexai.preview.reasoning_engines as reasoning_engines
except ImportError:
    # Graceful fallback for environments with older SDKs
    try:
        from google.cloud.aiplatform import reasoning_engines
    except ImportError:
        logging.warning("Reasoning Engine SDK not found. Cloud capabilities disabled.")
        reasoning_engines = None

# --- LOCAL MODULE IMPORTS ---
from ad_genius_capstone.tools.scraper_tool import scrape_website, read_pdf_content
from ad_genius_capstone.tools.ad_validator_tool import validate_ad_assets
from ad_genius_capstone.agents.strategist import get_strategist_agent
from ad_genius_capstone.agents.copywriter import get_copywriter_agent
from ad_genius_capstone.agents.validator import get_validator_agent

# --- CONFIGURATION ---
load_dotenv()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("AdGenius_Core")

# Constants
CLOUD_AGENT_ID = (
    "projects/247825145070/locations/europe-west1/reasoningEngines/8342971086261977088"
)
PROJECT_ID = "my-capstone-project-479616"
LOCATION = "europe-west1"

# --- HELPER FUNCTIONS ---


async def run_agent_execution(agent_def, prompt: str) -> str:
    """
    Executes an ADK agent within an isolated ephemeral session.
    """
    session_id = str(uuid.uuid4())
    user_id = "local_operator"
    app_name = "agents"

    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    runner = Runner(agent=agent_def, app_name=app_name, session_service=session_service)
    user_msg = types.Content(role="user", parts=[types.Part(text=prompt)])

    full_response = ""
    async for event in runner.run_async(
        session_id=session.id, user_id=user_id, new_message=user_msg
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    full_response += part.text
    return full_response


def extract_json(text: str):
    """
    Robust JSON extractor handling Markdown code blocks and raw text.
    """
    try:
        # 1. Try extracting from Markdown blocks
        match = re.search(r"``````", text, re.DOTALL)
        if match:
            return json.loads(match.group(1).strip())

        # 2. Try finding the first valid JSON object structure
        match_raw = re.search(r"(\{.*\})", text, re.DOTALL)
        if match_raw:
            return json.loads(match_raw.group(1))

        # 3. Attempt direct parse
        return json.loads(text)
    except Exception as e:
        logger.warning(f"JSON Extraction failed: {e}. Raw text sample: {text[:100]}...")
        return None


def save_results_to_csv(data: dict, url: str):
    """
    Exports generated ad assets to a timestamped CSV file.
    """
    rows = []
    for h in data.get("headlines", []):
        rows.append({"Type": "Headline", "Text": h, "Length": len(h)})
    for d in data.get("descriptions", []):
        rows.append({"Type": "Description", "Text": d, "Length": len(d)})

    # Generate clean filename
    clean_domain = url.split("//")[-1].split("/")[0].replace("www.", "")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"ads_{clean_domain}_{timestamp}.csv"

    pd.DataFrame(rows).to_csv(filename, index=False)
    logger.info(f"✅ Export successful: {filename}")


def query_cloud_strategist_engine(text_content: str):
    """
    Invokes the Vertex AI Agent Engine (Cloud Strategist).
    Returns raw response text or None if failure occurs.
    """
    if reasoning_engines is None:
        logger.warning("Cloud SDK unavailable. Skipping Cloud Engine.")
        return None

    logger.info(f"☁️ Invoking Cloud Strategist Agent ({CLOUD_AGENT_ID})...")
    try:
        aiplatform.init(project=PROJECT_ID, location=LOCATION)
        remote_agent = reasoning_engines.ReasoningEngine(CLOUD_AGENT_ID)
        response = remote_agent.query(input=text_content)
        return str(response)
    except Exception as e:
        logger.error(f"🔥 Cloud Engine Error: {e}")
        return None


# --- MAIN ORCHESTRATION LOOP ---


async def main():
    logger.info("🚀 AdGenius Orchestrator v1.0 Initialized")

    # Initialize Agents
    strategist_agent = get_strategist_agent()
    copywriter_agent = get_copywriter_agent()
    validator_agent = get_validator_agent()

    url = input("🌐 Target Website URL: ").strip()

    # --- PHASE 1: STRATEGIC ANALYSIS (HYBRID FAILOVER) ---

    USE_CLOUD_ENGINE = True  # Toggle for demonstration
    brief_response_text = ""

    # Step 1.1: Local Scraping (Used for both Cloud and Local analysis)
    logger.info("initiating scraping sequence...")
    scraped_text = scrape_website(url)

    # Handling Scraper Blocks immediately
    if "ERROR_NEED_HUMAN_HELP" in scraped_text:
        logger.warning("Scraping impeded. Automated Cloud analysis may degrade.")

    # Step 1.2: Cloud Execution
    if USE_CLOUD_ENGINE:
        # Truncate for token limits
        brief_response_text = query_cloud_strategist_engine(
            f"Analyze this text and generate a brief: {scraped_text[:30000]}"
        )

        if not brief_response_text or "Error" in str(brief_response_text):
            logger.warning(
                "⚠️ Cloud Engine Unreachable/Failed. Triggering Failover Protocol..."
            )
            USE_CLOUD_ENGINE = False

    # Step 1.3: Local Fallback Execution
    if not USE_CLOUD_ENGINE:
        logger.info("⚙️ Engaging Local Strategist Agent...")
        brief_response_text = await run_agent_execution(
            strategist_agent, f"Analyze this URL: {url}"
        )

        # PDF Fallback Logic
        if "CAPTCHA_DETECTED" in brief_response_text:
            logger.warning("CAPTCHA Challenge Active. Requesting User Intervention.")
            pdf_path_raw = input("📄 Please provide path to Homepage PDF: ").strip()
            # Sanitize path
            pdf_content = read_pdf_content(pdf_path_raw)

            if "SYSTEM_ERROR" in pdf_content:
                logger.error("Critical PDF Failure. Terminating.")
                return

            logger.info("Resuming analysis with PDF payload...")
            brief_response_text = await run_agent_execution(
                strategist_agent, pdf_content
            )

    # Step 1.4: Brief Extraction
    brief_json = extract_json(brief_response_text)
    if not brief_json:
        logger.error("Failed to extract valid JSON Brief. Aborting.")
        return

    logger.info(
        f"✅ Strategy Brief Generated: USP detected as '{brief_json.get('usp', 'N/A')[:50]}...'"
    )

    # --- PHASE 2: CREATIVE GENERATION ---
    logger.info("✍️ Engaging Copywriter Agent...")
    draft_text = await run_agent_execution(
        copywriter_agent, f"Here is the brief: {json.dumps(brief_json)}"
    )
    current_draft = extract_json(draft_text)

    # --- PHASE 3: SELF-CORRECTION LOOP (VALIDATION) ---
    MAX_RETRIES = 3
    for attempt in range(MAX_RETRIES):
        logger.info(f"👮‍♂️ Compliance Check {attempt+1}/{MAX_RETRIES}...")

        validation_result = await run_agent_execution(
            validator_agent, f"Validate: {json.dumps(current_draft)}"
        )

        if "FINAL_SUCCESS" in validation_result:
            logger.info("🎉 Validation Passed. Assets Approved.")
            save_results_to_csv(current_draft, url)
            break

        elif "FIX_REQUEST" in validation_result:
            logger.warning(f"Compliance Issues Detected. Retrying...")
            fix_prompt = f"Fix these specific errors:\n{validation_result}\n\nOutput the full corrected JSON."
            draft_text = await run_agent_execution(copywriter_agent, fix_prompt)
            current_draft = extract_json(draft_text)
        else:
            logger.error(f"Unknown Validation Signal: {validation_result}")
            break
    else:
        logger.error("❌ Max retries exceeded. Saving partial draft for review.")
        if current_draft:
            save_results_to_csv(current_draft, url + "_FAILED")


if __name__ == "__main__":
    asyncio.run(main())
