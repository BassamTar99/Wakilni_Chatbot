
import os
from jira import JIRA

jira = JIRA(
    server=os.getenv("JIRA_SERVER"),
    basic_auth=(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_TOKEN"))
)

def create_jira_issue(summary: str, description: str, issuetype: str="Task", project_key: str="WC") -> str:
    fields = {
        "project": {"key": project_key},
        "summary": summary,
        "description": description,
        "issuetype": {"name": issuetype},
    }
    issue = jira.create_issue(fields=fields)
    return issue.key

