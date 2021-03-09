import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from atlassian import Jira
import requests
import sys

env_path = Path('.') / '.env'

# load from file, if not read set env variables
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
nl = "\n"
try:
    SLACK_TOKEN = os.environ['SLACK_TOKEN']
    SLACK_CHANNEL = os.environ['SLACK_CHANNEL']
    JIRA_PROJECT = os.environ['JIRA_PROJECT']
    JIRA_USER = os.environ['JIRA_USER']
    JIRA_TOKEN = os.environ['JIRA_TOKEN']
    JIRA_SERVER = os.environ['JIRA_SERVER']
    JIRA_REVIEWER_FIELD = os.environ['JIRA_REVIEWER_FIELD']
except KeyError as error:
    sys.stderr.write('Please set the environment variable {0}'.format(error))
    sys.exit(1)

if 'ISSUE_PAGE_SIZE' in os.environ:
    ISSUE_PAGE_SIZE = os.environ['ISSUE_PAGE_SIZE']
else:
    ISSUE_PAGE_SIZE = 20

if 'SLACK_USERS_GROUP' in os.environ:
    SLACK_USERS_GROUP = os.environ['SLACK_USERS_GROUP']
else:
    SLACK_USERS_GROUP = None

if 'IGNORE_JIRA' in os.environ:
    IGNORE_JIRA = os.environ['IGNORE_JIRA']
else:
    IGNORE_JIRA = ""

if 'ISSUE_CHANGED_BEFORE' in os.environ:
    ISSUE_CHANGED_BEFORE = os.environ['ISSUE_CHANGED_BEFORE']
else:
    ISSUE_CHANGED_BEFORE = '-1d'

slack_client = slack.WebClient(token=SLACK_TOKEN)

jira = Jira(
    url=JIRA_SERVER,
    username=JIRA_USER,
    password=JIRA_TOKEN)

ignore_jira_set = set(IGNORE_JIRA.split(","))


def post_slack_message(prs, jira_id, reviewer_email, jira_summary):

    if reviewer_email != "":
        # get assign slack user details
        reviewer = slack_client.users_lookupByEmail(email=reviewer_email)
        # get slack user id
        reviewer_id = reviewer.get(key='user')['id']
    else:
        reviewer_id = SLACK_USERS_GROUP
    if prs != "":
        message = f'Hey :wave-animated: <@{reviewer_id}>! There is a pending jira review you should look at. :bow: {nl}' \
                  f'*Jira:* <{JIRA_SERVER}/browse/{jira_id}|{jira_summary}> {nl}{nl} *Pull Requests:* {nl}{prs}'
    else:
        message = f'Hey :wave-animated: <@{reviewer_id}>! There is a pending jira review you should look at. :bow: {nl}' \
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
                    url = pull_request['url']
                    pr_id = pull_request['id']
                    name = pull_request['name']
                    author = pull_request['author']['name']
                    prs = prs + separator + str(count) + ". " + f'<{url} | [PR: {pr_id}] {name} - by {author}>'
                    reviewers = extract_reviewers(pull_request)
                    if reviewers is not None:
                        prs = prs + nl + ' ' * 5 + f'*PR Reviewers:* {reviewers}'
                    separator = "\n\n"
                    count = count + 1
    return prs


def process_issue(issue):
    reviewer_email = ""
    jira_summary = ""
    jira_id = issue['key']
    if jira_id in ignore_jira_set:
        print(f'ignoring jira {jira_id}')
        return
    issue_id = issue['id']
    if JIRA_REVIEWER_FIELD in issue['fields']:
        reviewer_email = issue['fields'][JIRA_REVIEWER_FIELD]['emailAddress']
    if 'summary' in issue['fields']:
        jira_summary = issue['fields']['summary']
    if jira_summary == "":
        jira_summary = jira_id
    post_slack_message(get_open_pr(issue_id), jira_id, reviewer_email, jira_summary)


def process_in_review_jira():
    jql = f'project = {JIRA_PROJECT} AND status = "In Review" AND status CHANGED BEFORE {ISSUE_CHANGED_BEFORE} ORDER BY updatedDate ASC'
    data = jira.jql(jql, limit=ISSUE_PAGE_SIZE, fields=['id', 'key', 'summary', JIRA_REVIEWER_FIELD])
    all_issues = data['issues']
    for issue in all_issues:
        process_issue(issue)
    print("Completed!!")


if __name__ == '__main__':
    process_in_review_jira()
