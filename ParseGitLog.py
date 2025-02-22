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

#
# Get the git history from a git log. This code performs the equivalent to a git log --oneline --no-merges <soure>..<destination> to retrieve the history of
# changes in a code base between two tagged references
#

#Assumes you have access to the tags (have performed a git fetch of the repo)
def get_git_log(repo, repoName, source, destination):

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

    # Write the content of the commit messages into a CSV file of the form: <Hash>, <Jira_id>, <comment>
    with open('commitMessages.csv', 'w', newline='') as csvfile:
        commitWriter = csv.writer(csvfile, delimiter=',')
        commitWriter.writerow(['Hash', 'JiraId', 'Comment'])

        #Parse the git commit message to chunk into [hash, Jira number, comment]
        for line in lines:

            commitLine = splitCommitMessage(line)

            #Write the content of the parsed git log to a CSV file
            commitWriter.writerow([commitLine.hash, commitLine.jiraId, commitLine.comment])

            print(commitLine)

            print("---------------------------------------------")
'''
            #Developers like to add ':' next to jira id's, which throws off the ability to find the jira. Replace these with whitespace
            formattedLine = line.replace(":", " ")

            #Split the string on whitespace producing: [Hash, JiraId, comment]
            splittedString = formattedLine.split(" ", 2)          

            if(len(splittedString) > 2):

                #
                # Need to validate that the jira id is formatted correctly
                #
                jiraId = line.split("-", 2)
                if(len(jiraId) < 2):
                    print("Warning: the jira id is illformed, this entry shall be ignored:", line)
                
                #commitMessage = gitCommitMessage(splittedString[0], splittedString[1], splittedString[2])
                #commitWriter.writerow([commitMessage.hash, commitMessage.jiraId, commitMessage.comment])

                #Add the git commit entry into the git Dictionary, keyed on the Jira issue id
                ###-> gitDictionary[commitMessage.jiraId] = commitMessage
            else:
                print("Error parsing: not enough string to split", line)

                #These commit messages will be ignored.

def read_and_parse_git_commit_line():

    file = open('gitLogs_bp_to_18.csv', 'r')
    copyFile = open('gitLogs_bp_to_18_formatting.csv', 'w')
    errorFile = open('gitLog_errors.csv', 'w')


    for line in file:
        splittedString = line.split(" ", 2)

        if(len(splittedString) < 3):
            print("Error on line, not enough whitespace to split ", line)
            errorFile.write(line)
        else:
            copyLine = splittedString[0] + "," + splittedString[1] + "," + splittedString[2]
            copyFile.write(copyLine)
'''


def parse_csv_git_log():

    #
    # Input: A CSV file from a JQL query that is exported from Jira.
    #
    with open('gitLogs_bp_to_18_Final.csv', 'r') as inputCSVFile:
        csvReader = csv.DictReader(inputCSVFile, delimiter=",")

        for row in csvReader:
            entry = GitCommitEntry(**row)
            #gitDictionary[entry.jiraId] = entry;


def run_regex():
    print("Running my regex")
    regex = r"([a-f0-9]{6,8}) ([a-zA-Z0-9]+-[0-9]+)*.+"
    string = "aaaaaaa V500-1234 some message"
    match = re.findall(regex, string)  
    print(match)


def parse_csv_git_log():

    #
    # Input: A CSV file from a JQL query that is exported from Jira.
    #
    with open('gitLogs_bp_to_18_Final.csv', 'r') as inputCSVFile:
        csvReader = csv.DictReader(inputCSVFile, delimiter=",")

        for row in csvReader:
            entry = GitCommitEntry(**row)
            #gitDictionary[entry.jiraId] = entry;    

          
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
        

#if __name__ == "__main__":
#    run_regex()
