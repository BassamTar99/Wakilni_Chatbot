from dotenv import load_dotenv
load_dotenv()
import os
import requests

JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")
JIRA_SERVER = os.getenv("JIRA_SERVER")

url = f"{JIRA_SERVER}/rest/api/3/issue"
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}
auth = (JIRA_EMAIL, JIRA_TOKEN)
payload = {
    "fields": {
        "project": {"key": "WC"},
        "summary": "Test issue from API",
        "description": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "This is a test issue created via REST API."
                        }
                    ]
                }
            ]
        },
        "issuetype": {"name": "Task"}
    }
}
response = requests.post(url, json=payload, headers=headers, auth=auth)
print(f"Status code: {response.status_code}")
print(f"Response: {response.text}")
