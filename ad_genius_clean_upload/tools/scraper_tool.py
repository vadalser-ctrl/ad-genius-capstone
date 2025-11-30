import requests
import logging
from pypdf import PdfReader

# Configure logging for visibility
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def scrape_website(url: str) -> str:
    """
    Attempts to retrieve website content.
    Implements a 'Soft Fail' mechanism: if blocked (403, CAPTCHA),
    it returns a specific error signal to trigger the PDF Fallback workflow.
    """
    # Emulate a standard browser environment to ensure compatibility with modern web servers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }

    try:
        logger.info(f"Attempting to scrape: {url}")
        response = requests.get(url, headers=headers, timeout=15)

        # Check for explicit blocking signals
        if response.status_code in [403, 401, 500]:
            logger.warning(f"Access blocked with status {response.status_code}")
            return f"ERROR_NEED_HUMAN_HELP: Website blocked (Status {response.status_code}). Please upload PDF."

        content = response.text

        # Heuristic check for CAPTCHA or empty pages (soft block)
        if len(content) < 500:
            logger.warning(
                "Content length insufficient (<500 chars). Likely CAPTCHA challenge."
            )
            return "ERROR_NEED_HUMAN_HELP: Content too short. Possibly CAPTCHA. Please upload PDF."

        logger.info(f"Successfully scraped {len(content)} chars")
        return content[:15000]  # Truncate to preserve context window budget

    except Exception as e:
        logger.error(f"Scraper exception: {e}")
        return f"ERROR_NEED_HUMAN_HELP: Request failed ({str(e)}). Please upload PDF."


def read_pdf_content(file_path: str) -> str:
    """
    Reads and extracts text from a user-provided PDF file.
    Used as a fallback when direct scraping is not possible.
    """
    try:
        # Path Sanitization: Handle terminal drag-and-drop artifacts (quotes)
        clean_path = file_path.strip().strip("'").strip('"')

        reader = PdfReader(clean_path)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

        logger.info(f"PDF parsed successfully: {len(text)} chars extracted")

        # Prefix ensures the Strategist Agent correctly identifies the source
        return f"PDF_CONTENT_FROM_USER:\n{text[:15000]}"

    except Exception as e:
        logger.error(f"PDF Read Error: {e}")
        return f"SYSTEM_ERROR: Failed to read PDF at {file_path}. Error: {str(e)}"
