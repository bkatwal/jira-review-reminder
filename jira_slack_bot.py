import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from atlassian import Jira
import requests
from atlassian import Bitbucket

env_path = Path('.') / '.env'

# load from file, if not read set env variables
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
nl = "\n"
SLACK_TOKEN = os.environ['SLACK_TOKEN']
SLACK_CHANNEL = os.environ['SLACK_CHANNEL']
JIRA_PROJECT = os.environ['JIRA_PROJECT']
JIRA_USER = os.environ['JIRA_USER']
JIRA_TOKEN = os.environ['JIRA_TOKEN']
IGNORE_JIRA = os.environ['IGNORE_JIRA']
ISSUE_CHANGED_BEFORE = os.environ['ISSUE_CHANGED_BEFORE']
JIRA_SERVER = os.environ['JIRA_SERVER']
ISSUE_PAGE_SIZE = os.environ['ISSUE_PAGE_SIZE']
GIT_WORKSPACE = os.environ['GIT_WORKSPACE']
GIT_SERVER = os.environ['GIT_SERVER']
GIT_USER = os.environ['GIT_USER']
GIT_TOKEN = os.environ['GIT_TOKEN']

slack_client = slack.WebClient(token=SLACK_TOKEN)

jira = Jira(
    url=JIRA_SERVER,
    username=JIRA_USER,
    password=JIRA_TOKEN)


bitbucket = Bitbucket(
    url=GIT_SERVER,
    username=GIT_USER,
    password=GIT_TOKEN)

res = bitbucket.get_pull_requests(project_key='postmanlabs', repository_slug='00e989c3-3056-4273-922d-6d9ba893202f', pull_request_id=11139)
print(res)

ignore_jira_set = set(IGNORE_JIRA.split(","))


def post_slack_message(prs, jira_id, assignee_email, jira_summary):
    # get assign slack user details
    assignee = slack_client.users_lookupByEmail(email=assignee_email)

    # get slack user id
    assignee_id = assignee.get(key='user')['id']
    if prs != "":
        message = f'Hey :wave-animated: <@{assignee_id}>! A ticket assigned to you is in review state :bow: {nl}' \
                  f'*Jira:* <{JIRA_SERVER}/browse/{jira_id}|{jira_summary}> {nl}{nl} *Pull Requests:* {nl}{prs}'
    else:
        message = f'Hey :wave-animated: <@{assignee_id}>! A ticket assigned to you is in review state :bow: {nl}' \
                  f'*Jira:* <{JIRA_SERVER}/browse/{jira_id}|{jira_summary}> '

    partitioner = '-'*120
    slack_client.chat_postMessage(channel='#' + SLACK_CHANNEL, text=message + nl + partitioner)


def extract_reviewers(pull_request):
    reviewers = pull_request['reviewers']
    if len(reviewers) == 0:
        return None
    reviewers_str = ""
    separator = ""
    for reviewer in reviewers:
        reviewers_str = reviewers_str + separator + reviewer['name']
        separator = ", "
    return reviewers_str


def get_open_pr(issue_id):
    response = requests.get(
        url=f'{JIRA_SERVER}/rest/dev-status/latest/issue/details?issueId={issue_id}&applicationType=stash&dataType=pullrequest',
        auth=(JIRA_USER, JIRA_TOKEN))
    prs = ""
    details = response.json()['detail']
    separator = ""
    if details is None:
        return None
    count = 1
    for detail in details:
        if 'pullRequests' in detail:
            pull_requests = detail['pullRequests']
            for pull_request in pull_requests:
                if pull_request['status'] == 'OPEN':
                    prs = prs + separator + str(count) + ". " + pull_request['url']
                    reviewers = extract_reviewers(pull_request)
                    if reviewers is not None:
                        prs = prs + nl + ' ' * 5 + f'*PR Reviewers:* {reviewers}'
                    separator = "\n\n"
                    count = count + 1
    return prs


def process_issue(issue):
    assignee_email = ""
    jira_summary = ""
    jira_id = issue['key']
    if jira_id in ignore_jira_set:
        print(f'ignoring jira {jira_id}')
        return
    issue_id = issue['id']
    if 'assignee' in issue['fields']:
        assignee_email = issue['fields']['assignee']['emailAddress']
    if 'summary' in issue['fields']:
        jira_summary = issue['fields']['summary']
    if assignee_email == "":
        assignee_email = os.environ['SLACK_USERS_GROUP']
    post_slack_message(get_open_pr(issue_id), jira_id, assignee_email, jira_summary)


def process_in_review_jira():
    jql = f'project = {JIRA_PROJECT} AND status = "In Review" AND status CHANGED BEFORE {ISSUE_CHANGED_BEFORE} ORDER BY updatedDate ASC'
    data = jira.jql(jql, limit=ISSUE_PAGE_SIZE, fields=['id', 'key', 'summary', 'assignee'])
    all_issues = data['issues']
    for issue in all_issues:
        process_issue(issue)


if __name__ == '__main__':
    print("nothing")
    #process_in_review_jira()
