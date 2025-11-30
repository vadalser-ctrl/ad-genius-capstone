# AdGenius Capstone Project 🚀

**Automating High-Performance Google Ads Campaigns with Hybrid AI Agents**

![Status](https://img.shields.io/badge/Status-Production%20Ready-success)
![Stack](https://img.shields.io/badge/Tech-Google%20ADK%20%7C%20Gemini%202.5-blue)

---

## 💡 The Problem
Creating Google Ads campaigns manually is a bottleneck. Marketers struggle to balance **creativity** with **strict platform constraints** (character limits, policies). Furthermore, relying solely on cloud-based AI agents can be risky due to potential timeouts or API instability during high-load operations.

## 🛠️ The Solution: AdGenius
AdGenius is a robust, **failover-enabled orchestration system** that automates the entire ad creation lifecycle. It features a unique **Hybrid Architecture** that seamlessly switches between Google Cloud Vertex AI and a local reasoning engine to ensure 100% uptime.

### Key Features
*   **🔄 Hybrid Failover Core:** If the Cloud Strategist (Vertex AI) times out or fails, the system instantly activates a Local Strategist to complete the mission without data loss.
*   **🕵️ Stealth Scraping:** Custom tooling to extract marketing data from e-commerce sites, mimicking real user behavior to bypass soft blocks.
*   **👮 Self-Correction Loop:** A dedicated **Validator Agent** acts as a "Compliance Officer," rejecting any ad copy that violates Google's editorial policies (length, capitalization, punctuation) and forcing the Copywriter to rewrite it.
*   **📄 PDF Fallback:** Encountering a hard CAPTCHA? The system automatically requests a PDF upload and continues analysis seamlessly.

---

## 🏗️ Architecture

The system is composed of three specialized agents working in a loop:

1.  **Strategist Agent (The Brain):**
    *   Scrapes the URL or reads PDF.
    *   Analyzes the product to define USP, Audience, Tone, and Keywords.
    *   *Tech:* Gemini 2.5 Flash (Cloud/Local Hybrid).

2.  **Copywriter Agent (The Creative):**
    *   Takes the Brief and generates 15 Headlines and 4 Descriptions.
    *   Strictly follows the tone and keywords.

3.  **Validator Agent (The Enforcer):**
    *   Audits every character.
    *   Checks for: `Length > 30/90`, `ALL CAPS`, `Clickbait`, `Repetitive punctuation`.
    *   **Loop:** If rejected -> Sends feedback back to Copywriter -> Repeats until perfect.

---

## 🚀 How to Run

### Prerequisites
*   Python 3.10+
*   Google Cloud Project with Vertex AI API enabled
*   Gemini API Key

### Installation

1.  **Clone the repository:**
    ```
    git clone https://github.com/vadalser-ctrl/ad-genius-capstone.git
    cd ad_genius_clean_upload
    ```

2.  **Install dependencies:**
    ```
    pip install -r requirements.txt
    ```

3.  **Configure Environment:**
    Create a `.env` file and add your key:
    ```
    GOOGLE_API_KEY=your_key_here
    ```

4.  **Run the Orchestrator:**
    ```
    python main.py
    ```

---

## 📂 Project Structure

*   `main.py`: The central async orchestrator handling the Hybrid Loop.
*   `agents/`: Definitions for Strategist, Copywriter, and Validator.
*   `tools/`: Custom tools for scraping and policy validation.
*   `cloud_deploy_pkg/`: Configuration artifacts for Vertex AI Agent Engine deployment.

---

*Built for the Google AI Agents Intensive 2025 Capstone.*
