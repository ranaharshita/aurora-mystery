"""
agents.py - Multi-agent orchestration using Google GenAI SDK
"""

import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
import case_data
import prompts

# Load environment variables from .env
load_dotenv()

# Model selection - strictly gemini-3.6-flash as per requirements
MODEL_NAME = "gemini-3.6-flash"

def get_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it in your .env or environment.")
    return genai.Client(api_key=api_key)

def call_agent(client: genai.Client, system_instruction: str, user_content: str) -> str:
    """Helper call using google-genai SDK with thinking level set explicitly to low and transient error retries."""
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.2,
        thinking_config=types.ThinkingConfig(thinking_level="low")
    )

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=user_content,
                config=config
            )
            return response.text.strip()
        except Exception as e:
            err_str = str(e)
            # Do NOT retry 429 RESOURCE_EXHAUSTED or quota errors
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                raise e

            # Keep retry behavior for temporary 503/UNAVAILABLE errors
            if "503" in err_str or "UNAVAILABLE" in err_str:
                if attempt < max_retries - 1:
                    time.sleep(3 * (attempt + 1))
                    continue
            
            # Re-raise any other unhandled exception
            raise e

def format_agent_error(agent_name: str, exception: Exception) -> str:
    """Formats a clear error status message for a failed agent."""
    err_str = str(exception)
    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
        reason = "Gemini API quota exhausted for this project (429 RESOURCE_EXHAUSTED). The application and key configuration are working, but the model quota is currently unavailable."
    else:
        reason = f"Execution error: `{err_str}`"
    return f"⚠️ **{agent_name} Call Failed**\n\n{reason}"

def run_investigation(include_evidence_e: bool = True):
    """
    Runs the 5-agent sequential investigation pipeline.
    Incomplete investigations stop immediately and NEVER generate a Chief verdict.
    """
    client = get_client()
    raw_case_text = case_data.get_formatted_case_data(include_evidence_e=include_evidence_e)
    
    results = {
        "status": "INCOMPLETE",
        "status_message": "Investigation not started.",
        "detective": "Waiting for investigation run...",
        "evidence": "Waiting for investigation run...",
        "suspect": "Waiting for investigation run...",
        "skeptic": "Waiting for investigation run...",
        "chief": "🛑 **Chief Verdict Unavailable:** Investigation incomplete."
    }

    # Step 1: Detective Agent
    detective_input = f"{raw_case_text}\n\nTask: Reconstruct the timeline, list confirmed facts, analyze the critical time window, and state key open questions."
    try:
        results["detective"] = call_agent(client, prompts.DETECTIVE_PROMPT, detective_input)
    except Exception as e:
        results["status"] = "INCOMPLETE"
        results["status_message"] = "Investigation Incomplete — Detective Agent failed."
        results["detective"] = format_agent_error("Detective Agent", e)
        results["evidence"] = "🛑 **Skipped:** Stopped because Detective Agent failed."
        results["suspect"] = "🛑 **Skipped:** Stopped because Detective Agent failed."
        results["skeptic"] = "🛑 **Skipped:** Stopped because Detective Agent failed."
        results["chief"] = "🛑 **Chief Verdict Unavailable:** Stopped because Detective Agent failed."
        return results

    # Step 2: Evidence Evaluator Agent
    if include_evidence_e:
        evidence_task = "Task: Evaluate Evidence A through G."
    else:
        evidence_task = "Task: Evaluate Evidence A through G. Note that Evidence E has been removed from this run and must NOT be used or relied upon."
    evidence_input = f"{raw_case_text}\n\n--- DETECTIVE REPORT ---\n{results['detective']}\n\n{evidence_task}"
    try:
        results["evidence"] = call_agent(client, prompts.EVIDENCE_PROMPT, evidence_input)
    except Exception as e:
        results["status"] = "INCOMPLETE"
        results["status_message"] = "Investigation Incomplete — Evidence Evaluator Agent failed."
        results["evidence"] = format_agent_error("Evidence Evaluator Agent", e)
        results["suspect"] = "🛑 **Skipped:** Stopped because Evidence Evaluator Agent failed."
        results["skeptic"] = "🛑 **Skipped:** Stopped because Evidence Evaluator Agent failed."
        results["chief"] = "🛑 **Chief Verdict Unavailable:** Stopped because Evidence Evaluator Agent failed."
        return results

    # Step 3: Suspect Agent
    suspect_input = f"{raw_case_text}\n\n--- DETECTIVE REPORT ---\n{results['detective']}\n\n--- EVIDENCE REPORT ---\n{results['evidence']}\n\nTask: Compare all four suspects."
    try:
        results["suspect"] = call_agent(client, prompts.SUSPECT_PROMPT, suspect_input)
    except Exception as e:
        results["status"] = "INCOMPLETE"
        results["status_message"] = "Investigation Incomplete — Suspect Profiler Agent failed."
        results["suspect"] = format_agent_error("Suspect Profiler Agent", e)
        results["skeptic"] = "🛑 **Skipped:** Stopped because Suspect Profiler Agent failed."
        results["chief"] = "🛑 **Chief Verdict Unavailable:** Stopped because Suspect Profiler Agent failed."
        return results

    # Step 4: Skeptic Agent
    skeptic_input = f"{raw_case_text}\n\n--- DETECTIVE REPORT ---\n{results['detective']}\n\n--- EVIDENCE REPORT ---\n{results['evidence']}\n\n--- SUSPECT REPORT ---\n{results['suspect']}\n\nTask: Challenge the leading theory and card-access assumption."
    try:
        results["skeptic"] = call_agent(client, prompts.SKEPTIC_PROMPT, skeptic_input)
    except Exception as e:
        results["status"] = "INCOMPLETE"
        results["status_message"] = "Investigation Incomplete — Skeptic Agent failed."
        results["skeptic"] = format_agent_error("Skeptic Agent", e)
        results["chief"] = "🛑 **Chief Verdict Unavailable:** Stopped because Skeptic Agent failed."
        return results

    # Step 5: Chief Investigator Agent (Only reached if all 4 specialists completed successfully)
    chief_input = f"{raw_case_text}\n\n--- DETECTIVE REPORT ---\n{results['detective']}\n\n--- EVIDENCE REPORT ---\n{results['evidence']}\n\n--- SUSPECT REPORT ---\n{results['suspect']}\n\n--- SKEPTIC REPORT ---\n{results['skeptic']}\n\nTask: Produce the final Chief Verdict & Summary."
    try:
        results["chief"] = call_agent(client, prompts.CHIEF_PROMPT, chief_input)
        results["status"] = "COMPLETED"
        results["status_message"] = "Investigation Complete — All 5 specialists finished successfully."
    except Exception as e:
        results["status"] = "INCOMPLETE"
        results["status_message"] = "Investigation Incomplete — Chief Agent failed."
        results["chief"] = f"🛑 **Chief Verdict Unavailable**\n\n{format_agent_error('Chief Investigator Agent', e)}"
        return results

    return results


