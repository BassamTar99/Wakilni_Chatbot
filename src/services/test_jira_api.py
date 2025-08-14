import os
from agent_tools import get_jira_issue, list_jira_issues, update_jira_issue, transition_jira_issue

# Set up environment (if not already loaded)
from dotenv import load_dotenv
load_dotenv()

# Test get_jira_issue
issue_key = input("Enter JIRA issue key to fetch (e.g., WC-1): ")
print("Fetching issue details...")
issue = get_jira_issue(issue_key)
if 'error' in issue:
    print(f"Error: {issue['error']}")
else:
    fields = issue.get('fields', {})
    print(f"Issue Key: {issue.get('key', '')}")
    print(f"Title: {fields.get('summary', '')}")
    print(f"Status: {fields.get('status', {}).get('name', '')}")
    print(f"Last Updated: {fields.get('updated', '')}")

# Test list_jira_issues
jql = input("Enter JQL to list issues (e.g., project=WC): ")
print("Listing issues...")
issues = list_jira_issues(jql)
if 'error' in issues:
    print(f"Error: {issues['error']}")
else:
    for issue in issues.get('issues', []):
        fields = issue.get('fields', {})
        print("---------------------------")
        print(f"Issue Key: {issue.get('key', '')}")
        print(f"Title: {fields.get('summary', '')}")
        print(f"Status: {fields.get('status', {}).get('name', '')}")
        print(f"Last Updated: {fields.get('updated', '')}")

# Test update_jira_issue
update = input("Update issue? (y/n): ")
if update.lower() == "y":
    field = input("Field to update (e.g., summary): ")
    value = input("New value: ")
    print("Updating issue...")
    result = update_jira_issue(issue_key, {field: value})
    print(result)

# Test transition_jira_issue
transition = input("Transition issue? (y/n): ")
if transition.lower() == "y":
    transition_id = input("Transition ID (e.g., 31 for Done): ")
    print("Transitioning issue...")
    result = transition_jira_issue(issue_key, transition_id)
    print(result)
