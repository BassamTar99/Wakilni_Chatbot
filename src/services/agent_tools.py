"""
agent_tools.py: Tool wrappers for agentic AI support bot
"""
import requests
from bs4 import BeautifulSoup

# Tool 1: fetch_page

def fetch_page(url: str) -> str:
    """Retrieve a documentation or error page by URL."""
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text

# Tool 2: parse_requirements

def parse_requirements(html: str) -> dict:
    """Extract structured requirements from a docs page (min_version, required_fields)."""
    soup = BeautifulSoup(html, 'html.parser')
    # Example extraction logic (customize for your docs)
    min_version = None
    required_fields = []
    for tag in soup.find_all(['p', 'li']):
        text = tag.get_text().lower()
        if 'minimum version' in text:
            min_version = text.split('minimum version')[-1].strip(': .')
        if 'required field' in text:
            required_fields.append(text.split('required field')[-1].strip(': .'))
    return {"min_version": min_version, "required_fields": required_fields}

# Tool 3: run_diagnostics

def run_diagnostics() -> dict:
    """Call internal health-check/status API."""
    # Example: Replace with your actual healthcheck endpoint
    resp = requests.get("https://wakilni.com/api/health", timeout=5)
    resp.raise_for_status()
    return resp.json()

# Tool 4: lookup_faq

def lookup_faq(query: str) -> list:
    """Query FAQ vector store for top-n similar entries."""
    # Placeholder: Replace with your actual FAQ search logic
    # Example: return [{"question": "...", "answer": "..."}, ...]
    return []

# Tool 5: create_jira_issue

def create_jira_issue(summary: str, description: str, priority: str) -> dict:
    """Open a new Jira ticket for actionable problems."""
    # Placeholder: Replace with your actual Jira integration
    # Example: return {"key": "WC-123"}
    return {"key": "WC-123"}
