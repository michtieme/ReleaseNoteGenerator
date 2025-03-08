#For calling Git commands
import re
import os
import dataclasses
import csv

#
# GitPython
#
import git

#
# Class to hold a git commit message of the form: <hash> <jiraId> <comment>
#
@dataclasses.dataclass
class GitCommitMessage:
    """Class to encapsulate the content of a git log line"""
    def __init__(self, sha_hash, jira_id, comment):
        self.hash = sha_hash
        self.jira_id = jira_id
        self.comment = comment

    def __str__(self):
        return "[" + self.hash + "],[" + self.jira_id + "],[" + self.comment + "]"

#
# Get the git history from a git log. This code performs the equivalent to a git log --oneline --no-merges <soure>..<destination> to retrieve the history of
# changes in a code base between two tagged references
#

#Assumes you have access to the tags (have performed a git fetch of the repo)
def get_git_log(repo, repo_name, source, destination):
    """Get the content of the git log from a repo between a source and destination tag"""

    write_git_log = True
    commit_dictionary = {}

    #Location of the repo
    repo_directory = os.path.join(os.path.abspath(repo), repo_name)

    #TODO: Handle errors when unable to retreive the git log

    #Set the repo
    repo = git.Repo(repo_directory)

    #
    # Equivalent to: git log --oneline --nomerges --no-decorate <source>..<dest>
    #
    logs = repo.git.log("--oneline", "--no-merges", "--no-decorate", source + ".." + destination)
    lines = logs.splitlines()
    full_log = ''

    git_log_command = 'git log --oneline --no-merges --no-decorate ' + source + '..' + destination + '\n'

    # Parse out all the commits into a list
    commits = []
    for line in lines:
        commit = split_commit_message(line)
        commits.append(commit)
        full_log += line + '\n'

        # There can be multiple commit messages per Jira id. Collect the commit messages in a list
        if(commit.jira_id in commit_dictionary):
            commit_dictionary[commit.jira_id].append(commit)
        else:
            commit_dictionary[commit.jira_id] = [commit]

    # Optionally write all the commits into a CSV file of the form: <Hash>, <Jira_id>, <comment>
    if write_git_log:

        with open('commitMessages.csv', 'w', newline='') as csvfile:
            commit_writer = csv.writer(csvfile, delimiter=',')
            commit_writer.writerow(['Hash', 'JiraId', 'Comment'])

            for commit in commits:
                commit_writer.writerow([commit.hash, commit.jira_id, commit.comment])

    return commit_dictionary, git_log_command, full_log


def split_commit_message(git_commit_line):
    """parse the git commit message to extract the hash, jira_id and message from git log entry"""

    sha_regex = r"([a-f0-9]{6,120})"
    sha_match = re.findall(sha_regex, git_commit_line)

    #Didn't even find the sha hash, return an empty string
    if(len(sha_match) == 0):
        return GitCommitMessage("", "UNKNOWN", git_commit_line)

    #Trim off the sha1
    commit_message = git_commit_line.removeprefix(sha_match[0])

    #Try to match the jira id and the commit message
    regex = r"([\s]([a-zA-Z0-9]+-[0-9]+)(.+))"
    match = re.findall(regex, commit_message)

    #Did not find the jira id from the regex
    if(len(match) == 0):

        #Its a common mistake to replace the '-' with a ':' in the jira-id, try to match this instead
        alternative_regex = r"([\s]([a-zA-Z0-9]+:[0-9]+)[\s](.+))"
        alternative_match = re.findall(alternative_regex, commit_message)
        commit_message = trim_excess_prefix_characters(commit_message)

        #Didn't match any style of malformed jira-id's (jira-id is missing)
        if(len(alternative_match) == 0):
            return GitCommitMessage(sha_match[0], "UNKNOWN", commit_message)

        #Fix up the jira-id by replacing the incorrect characters
        fixed_jira_id = alternative_match[0][1]
        fixed_jira_id = fixed_jira_id.replace(':', '-')
        commit_message = trim_excess_prefix_characters(alternative_match[0][2])

        return GitCommitMessage(sha_match[0], fixed_jira_id, commit_message)

    #Alternatively, found a tuple of the matched ranges
    tuple_of_matches = match[0]

    if(len(tuple_of_matches) != 3):
        print("Did not match the regex - wrong tuple size")
        print(commit_message)
        return GitCommitMessage("UNKNOWN", "UNKNOWN", "UNKNOWN")
    else:
        sha = sha_match[0]
        jira_id = tuple_of_matches[1]
        message = trim_excess_prefix_characters(tuple_of_matches[2])

    return GitCommitMessage(sha, jira_id, message)

def trim_excess_prefix_characters(message):
    """trim any leading ':' or '-' characters, or whitespace"""
    return message.lstrip(",:- ")

