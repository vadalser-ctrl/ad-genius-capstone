from typing import List, Dict, Any
import re


def validate_ad_assets(headlines: List[str], descriptions: List[str]) -> Dict[str, Any]:
    """
    Validates Google Ads assets against technical constraints and editorial policies.

    Checks performed:
    - Length constraints (Headlines: 30, Descriptions: 90)
    - Excessive Capitalization (e.g., ALL CAPS)
    - Editorial Standards (No exclamation marks in headlines, no repetitive punctuation)
    - Duplicate assets
    """
    errors = []

    # Basic simplified patterns to flag potential policy issues
    # Note: In a real production system, this would be more extensive.
    clickbait_patterns = [r"click here", r"buy now", r"best\s"]

    # --- 1. HEADLINES VALIDATION ---
    if headlines:
        for i, h in enumerate(headlines):
            # Length Check
            if len(h) > 30:
                errors.append(
                    f"Headline #{i+1} '{h}' exceeds limit ({len(h)}/30 chars)."
                )

            # Capitalization Check (Allow acronyms <= 4 chars)
            if h.isupper() and len(h) > 4:
                errors.append(
                    f"Headline #{i+1} '{h}' has excessive capitalization (Policy Violation)."
                )

            # Punctuation Check
            if "!" in h:
                errors.append(
                    f"Headline #{i+1} '{h}' contains '!'. Exclamation marks are not allowed in headlines."
                )

    # --- 2. DESCRIPTIONS VALIDATION ---
    if descriptions:
        for i, d in enumerate(descriptions):
            # Length Check
            if len(d) > 90:
                errors.append(
                    f"Description #{i+1} '{d}' exceeds limit ({len(d)}/90 chars)."
                )

            # Repetitive Punctuation Check (e.g., !!!, ???)
            if re.search(r"[!?.]{2,}", d):
                errors.append(
                    f"Description #{i+1} '{d}' contains excessive punctuation."
                )

            # Capitalization Check
            if d.isupper():
                errors.append(
                    f"Description #{i+1} uses excessive capitalization. Please use sentence case."
                )

    # --- 3. DUPLICATE CHECK ---
    # Google Ads requires unique assets for variety and performance optimization.
    if len(headlines) != len(set(headlines)):
        errors.append(
            "Duplicate headlines detected. Assets must be unique to maximize ad strength."
        )

    # --- VERDICT GENERATION ---
    if errors:
        return {
            "status": "REJECTED",
            "feedback": "Policy Violations Detected:\n" + "\n".join(errors),
        }
    else:
        return {
            "status": "APPROVED",
            "feedback": "All assets are valid and policy-compliant.",
        }
