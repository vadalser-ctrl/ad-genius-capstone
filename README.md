# AdGenius Capstone Project 🚀

**Google Ads Automation with a Hybrid AI Twist**

![Status](https://img.shields.io/badge/Status-Works%20on%20My%20Machine-success)
![Stack](https://img.shields.io/badge/Tech-Google%20ADK%20%7C%20Gemini%202.5-blue)

---

## 💡 Why I Built This
Writing Google Ads manually is painful. You have to be creative, but also count every character (30 for headlines, 90 for descriptions). One mistake, and Google rejects it. 

I wanted to build a system that does the boring work for me. But during development, I noticed that Cloud Agents can sometimes be slow or timeout. So, I built something special to fix that.

## 🛠️ What is AdGenius?
It's a multi-agent system that writes perfect Google Ads campaigns. It reads a website, figures out the strategy, writes the ads, and then **checks itself** to make sure everything is compliant.

**The Cool Part (Hybrid Architecture):**
The system tries to use Google Vertex AI (Cloud) first. But if the cloud is unreachable or errors out, it doesn't crash. It automatically switches to a **Local Agent** running on my machine. Zero downtime.

### Key Features
*   **🔄 "Cloud-to-Local" Switch:** The script detects cloud errors and instantly switches to local processing. It just works.
*   **🕵️ Smart Scraper:** Extracts data even from tricky websites.
*   **👮 The Validator Agent:** I built a "strict boss" agent. It checks character limits and policies. If the Copywriter messes up (e.g., uses ALL CAPS), the Validator rejects it and forces a rewrite.
*   **📄 PDF Backup:** If a website blocks the scraper completely, the system asks for a PDF upload and continues.

---

## 🏗️ How It Works (The Loop)

1.  **Strategist Agent:** Reads the website (or PDF) and writes a Brief (Who is the audience? What is the tone?).
2.  **Copywriter Agent:** Writes 15 Headlines and 4 Descriptions based on the Brief.
3.  **Validator Agent:** The most important part. It loops until the ads are 100% correct and fit the limits.

---

## 🚀 How to Run

### Prerequisites
*   Python 3.10+
*   Google Cloud Project (for Vertex AI)
*   Gemini API Key

### Installation

1.  **Clone the repo:**
    ```
    git clone https://github.com/vadalser-ctrl/ad-genius-capstone.git
    cd ad_genius_clean_upload
    ```

2.  **Install requirements:**
    ```
    pip install -r requirements.txt
    ```

3.  **Set up API Key:**
    Create a `.env` file:
    ```
    GOOGLE_API_KEY=your_key_here
    ```

4.  **Run it:**
    ```
    python main.py
    ```

---

## 📂 Folder Structure

*   `main.py`: The main script that runs everything.
*   `agents/`: The code for my 3 agents.
*   `tools/`: Tools for scraping and checking ad length.
*   `cloud_deploy_pkg/`: Files I used to deploy the agent to Google Cloud.

---

*Built for the Google AI Agents Intensive 2025 Capstone.*
