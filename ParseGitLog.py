#For calling Git commands
import re
import os

import csv

#
# GitPython
#
import git

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
def get_git_log(repo, repo_name, source, destination):

    write_git_log = True
    commit_dictionary = {}

    #Location of the repo
    repo_directory = os.path.join(os.path.abspath(repo), repo_name)

    #Set the repo
    repo = git.Repo(repo_directory)

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
        commit_dictionary[commit.jira_id] = commit

    # Optionally write all the commits into a CSV file of the form: <Hash>, <Jira_id>, <comment>
    if (write_git_log):

        with open('commitMessages.csv', 'w', newline='') as csvfile:
            commit_writer = csv.writer(csvfile, delimiter=',')
            commit_writer.writerow(['Hash', 'JiraId', 'Comment'])

            for commit in commits:
                commit_writer.writerow([commit.hash, commit.jira_id, commit.comment])

    return commit_dictionary


def splitCommitMessage(gitCommitLine):

    sha_regex = r"([a-f0-9]{6,120})"
    sha_match = re.findall(sha_regex, gitCommitLine)

    #Didn't even find the sha hash, return an empty string
    if(len(sha_match) == 0):
        return gitCommitMessage("", "", "")

    #Trim off the sha1
    commit_message = gitCommitLine.removeprefix(sha_match[0])

    #Try to match the jira id and the commit message
    regex = r"([\s]([a-zA-Z0-9]+-[0-9]+)(.+))"
    match = re.findall(regex, commit_message)

    #Did not find the jira id from the regex
    if(len(match) == 0):

        #Its a common mistake to replace the '-' with a ':' in the jira-id, try to match this instead
        alternative_regex = r"([\s]([a-zA-Z0-9]+:[0-9]+)(.+))"
        match = re.findall(alternative_regex, commit_message)

        commit_message = trim_excess_prefix_characters(commit_message)

        #Didn't match any style of malformed jira-id's (jira-id is missing)
        if(len(match) == 0):
            return gitCommitMessage(sha_match[0], "UNKNOWN", commit_message)

        #Fix up the jira-id by replacing the incorrect characters
        fixed_jira_id = match[0][1]
        fixed_jira_id = fixed_jira_id.replace(':', '-')
        return gitCommitMessage(sha_match[0], fixed_jira_id, commit_message)

    #Alternatively, had to find a tuple of the matched ranges
    tuple_of_matches = match[0]

    if(len(tuple_of_matches) != 3):
        print("Did not match the regex - wrong tuple size")
        print(commit_message)
        return gitCommitMessage("UNKNOWN", "UNKNOWN", "UNKNOWN")
    else:
        sha = sha_match[0]
        jira_id = tuple_of_matches[1]
        message = trim_excess_prefix_characters(tuple_of_matches[2])

    return gitCommitMessage(sha, jira_id, message)

def trim_excess_prefix_characters(message):
    #trim any leading ':' or '-' characters, or whitespace
	return message.lstrip(",:- ")

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
