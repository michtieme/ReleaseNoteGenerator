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

    def __init__(self, hash, jiraId, comment):
        self.hash = hash
        self.jiraId = jiraId
        self.comment = comment
 
    def __str__(self):
        return "[" + self.hash + "],[" + self.jiraId + "],[" + self.comment + "]"
    
class GitCommitEntry:

# CSV Header:    
# hash, issue_id, summary

    def __init__(self, **kwargs):
        self.hash = kwargs.get('hash')
        self.jiraId = kwargs.get('jiraId')
        self.comment = kwargs.get('comment')

    def __str__(self):
        return self.hash + " " + self.Issue_id + " " + self.Summary      

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
    #perform a git fetch
    #
    # TODO: git fetch bombs out. Needs some investigation
    #for remote in repo.remotes:
    #    remote.fetch()

    #
    # Equivalent to: git log --oneline --nomerges $source..$dest
    #
    logs = repo.git.log("--oneline", "--no-merges", source + ".." + destination)
    lines = logs.splitlines()

    # Parse out all the commits into a list
    commits = []
    for line in lines:
        commit = splitCommitMessage(line)    
        commits.append(commit)
        gitDictionary[commit.jiraId] = commit

    print("========================================================")
    for entry in gitDictionary:
        print(entry + " " + str(gitDictionary[entry]))

    # Optionally write all the commits into a CSV file of the form: <Hash>, <Jira_id>, <comment>
    if (writeLog):

        with open('commitMessages.csv', 'w', newline='') as csvfile:
            commitWriter = csv.writer(csvfile, delimiter=',')
            commitWriter.writerow(['Hash', 'JiraId', 'Comment'])
            
            for commit in commits:
                commitWriter.writerow([commit.hash, commit.jiraId, commit.comment])

    return gitDictionary                

          
def splitCommitMessage(gitCommitLine):

    regex = r"(([a-f0-9]{6,8}) ([a-zA-Z0-9]+-[0-9]+)(.+))"
    match = re.findall(regex, gitCommitLine)

    #Did not match the regex
    if(len(match) == 0):
        print("Did not match the regex")
        print(gitCommitLine)
        return gitCommitMessage("a", "b", "c")

    tuple = match[0]    

    if(len(tuple) != 4):
        print("Did not match the regex")
        print(gitCommitLine)
        return gitCommitMessage("d", "e", "f")
    else:        

        sha = tuple[1]
        jiraId = tuple[2]
        message = tuple[3]
        
    return gitCommitMessage(sha, jiraId, message)
        

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
