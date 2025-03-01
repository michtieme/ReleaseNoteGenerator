#For calling Git commands
import re
import os

import csv

#
# GitPython
#
import git
from git import Repo

#
# Class to hold a git commit message of the form: <hash> <jiraId> <comment>
#
class gitCommitMessage:

    def __init__(self, hash, jira_id, comment):
        self.hash = hash
        self.jira_id = jira_id
        self.comment = comment

    def __str__(self):
        return "[" + self.hash + "],[" + self.jira_id + "],[" + self.comment + "]"

class GitCommitEntry:

# CSV Header:
# hash, issue_id, summary

    def __init__(self, **kwargs):
        self.hash = kwargs.get('hash')
        self.jira_id = kwargs.get('jiraId')
        self.comment = kwargs.get('comment')

    def __str__(self):
        return self.hash + " " + self.jira_id + " " + self.comment

#
# Get the git history from a git log. This code performs the equivalent to a git log --oneline --no-merges <soure>..<destination> to retrieve the history of
# changes in a code base between two tagged references
#

#Assumes you have access to the tags (have performed a git fetch of the repo)
def get_git_log(repo, repoName, source, destination):

    writeLog = True
    gitDictionary = {}

    #Location of the repo
    repoDir = os.path.join(os.path.abspath(repo), repoName)

    #Set the repo
    repo = git.Repo(repoDir)

    #
    # Equivalent to: git log --oneline --nomerges --no-decorate <source>..<dest>
    #
    logs = repo.git.log("--oneline", "--no-merges", "--no-decorate", source + ".." + destination)
    lines = logs.splitlines()

    # Parse out all the commits into a list
    commits = []
    for line in lines:
        commit = splitCommitMessage(line)
        commits.append(commit)
        gitDictionary[commit.jira_id] = commit

    print("========================================================")
    for entry in gitDictionary:
        print(entry + " " + str(gitDictionary[entry]))

    # Optionally write all the commits into a CSV file of the form: <Hash>, <Jira_id>, <comment>
    if (writeLog):

        with open('commitMessages.csv', 'w', newline='') as csvfile:
            commitWriter = csv.writer(csvfile, delimiter=',')
            commitWriter.writerow(['Hash', 'JiraId', 'Comment'])

            for commit in commits:
                commitWriter.writerow([commit.hash, commit.jira_id, commit.comment])

    return gitDictionary


def splitCommitMessage(gitCommitLine):

    sha_regex = r"([a-f0-9]{6,120})"
    shaMatch = re.findall(sha_regex, gitCommitLine)

    #Didn't even find the sha hash, return an empty string
    if(len(shaMatch) == 0):
        return gitCommitMessage("", "", "")

    #Trim off the sha1
    commitMessage = gitCommitLine.removeprefix(shaMatch[0])

    #Try to match the jira id and the commit message
    regex = r"([\s]([a-zA-Z0-9]+-[0-9]+)(.+))"
    match = re.findall(regex, commitMessage)

    #Did not find the jira id from the regex
    if(len(match) == 0):

        #Its a common mistake to replace the '-' with a ':' in the jira-id, try to match this instead
        alternative_regex = r"([\s]([a-zA-Z0-9]+:[0-9]+)(.+))"
        match = re.findall(alternative_regex, commitMessage)

        commitmessage = trim_excess_prefix_characters(commitMessage)

        #Didn't match any style of malformed jira-id's
        if(len(match) == 0):
            return gitCommitMessage(shaMatch[0], "UNKNOWN", commitMessage)

        #Fix up the jira-id by replacing the incorrect characters
        fixedJiraId = match[0][1]
        fixedJiraId = fixedJiraId.replace(':', '-')
        return gitCommitMessage(shaMatch[0], fixedJiraId, commitMessage)

    #Alternatively, had to find a tuple of the matched ranges
    tuple = match[0]

    if(len(tuple) != 3):
        print("Did not match the regex - wrong tuple size")
        print(commitMessage)
        return gitCommitMessage("d", "e", "f")
    else:
        sha = shaMatch[0]
        jiraId = tuple[1]
        message = trim_excess_prefix_characters(tuple[2])

    return gitCommitMessage(sha, jiraId, message)

def trim_excess_prefix_characters(message):
    #trim any leading ':' or '-' characters, or whitespace
	return message.lstrip(":- ")

def parse_csv_git_log(fileName):

    #
    # Input: A CSV file from a JQL query that is exported from Jira.
    #
    with open(fileName, 'r') as inputCSVFile:
        csvReader = csv.DictReader(inputCSVFile, delimiter=",")

        for row in csvReader:
            entry = GitCommitEntry(**row)
            print(entry)


if __name__ == "__main__":
    parse_csv_git_log("commitMessagesToParse.csv")
