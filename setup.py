import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name='jira-reviews-reminder',
    version='0.1.3',
    url='https://github.com/bkatwal/jira-review-reminder',
    author='Bikas Katwal',
    author_email='bikas.katwal10@gmail.com',
    description='Notifies in Slack channel with a list of jira tickets that have pending review from x days. Adds the reviewer and PR details if exists.',
    long_description=long_description,
    py_modules=['jira_review_reminder'],
    license='MIT',
    python_requires='>=3',
    install_requires=[
        'requests==2.25.1',
        'slackclient==2.9.3',
        'atlassian-python-api==3.6.0',
        'python-dotenv==0.15.0'
    ],
    entry_points='''
        [console_scripts]
        jira-reviews-reminder=jira_review_reminder:process_in_review_jira
    '''
)