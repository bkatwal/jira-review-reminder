# Slack Bot Jira Review Reminder
Notifies in Slack channel with a list of jira tickets that have pending review from x days. Adds the reviewer and PR details if exists.
> Reviewer's names will be tagged in Slack notifications only if Jira email and slack email are same for all users
### Installation
```buildoutcfg
pip install jira-reviews-reminder
```
### Usage

After installing the package run below command:
```buildoutcfg
SLACK_TOKEN=XXXXXXXX SLACK_CHANNEL=catalog-team JIRA_PROJECT=catalog-proj JIRA_USER=abc@org.com JIRA_TOKEN=XXXXXX JIRA_SERVER=https://org.atlassian.net JIRA_REVIEWER_FIELD=customfield_10200 jira-reviews-reminder
```
This script will run and exit. So, preferably schedule a cron job.

#### Example:
To run every day 11 AM and 5 PM
```buildoutcfg
0 11,17 * * *  SLACK_TOKEN=XXXXXXXX SLACK_CHANNEL=catalog-team JIRA_PROJECT=catalog-proj JIRA_USER=abc@org.com JIRA_TOKEN=XXXXXX JIRA_SERVER=https://org.atlassian.net JIRA_REVIEWER_FIELD=customfield_10200 jira-reviews-reminder
```

### Environment Variables

##### SLACK_TOKEN
Create a slack bot app and get the Bot User OAuth Token. Use it as Env variable.

<a href="https://slack.com/intl/en-in/help/articles/115005265703-Create-a-bot-for-your-workspace">Instructions to create Slack Bot</a>

> Make sure your bot has all necessary permissions/scopes:
> `users:read.email`, `chat:write.public`, `channels:read`, `channels:join`

##### SLACK_CHANNEL
Slack channel of your team/jira project. No need to prefix with `#`

##### JIRA_PROJECT
The jira project key of your team. Tickets belonging to these projects will be processed.

TODO: Pass comma separated projects, if multiple projects need to be assessed. 

##### JIRA_USER and JIRA_TOKEN
Jira user ID/email and user/app token - need this to authorize the jira client.

##### IGNORE_JIRA (Optional)
Comma separated Jira IDs. Any jira ID passed in this env variable will not be processed.

##### ISSUE_CHANGED_BEFORE (Optional)
This variable is used to trigger reminder if the ticket is in review state from x unti of time.

Example: 
If the variable value is `-1d`. Only those jira will be processed which are in `In Review` state for more than 1 day.

>default to `-1d`

##### JIRA_SERVER
Jira hosted server - to establish connection.

Example: https://something.atlassian.net

##### ISSUE_PAGE_SIZE (Optional)
Maximum number of issues to assess that are `In review`.
> defaults to 20

##### SLACK_USERS_GROUP (Optional)
This is your team's slack user group. If a ticket doesn't have any reviewer, this user group is tagged in Slack notification.

##### JIRA_REVIEWER_FIELD
A few of the attributes in jira ticket are placed in dynamic fields/custom fields. This could be different for different projects.

Find out which field in the API response corresponds to the `Reviewers` field.

Example: `customfield_10200`

API Details:
> GET /rest/api/2/issue/your_jira_ID

### LICENSE

--------------
The MIT License (MIT)

Copyright (c) Bikas Katwal - bikas.katwal10@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
