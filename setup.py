import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
     name='jira-review-reminder',
     version='0.1',
     scripts=['reminder_bot'],
     author="Bikas Katwal",
     author_email="bikas.katwal10@gmail.com",
     description="Notifies in Slack channel with a list of jira tickets that have pending review from x days. Adds the reviewer and PR details if exists.",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/bkatwal/jira-review-reminder",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )