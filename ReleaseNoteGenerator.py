
import csv

#For calling Git commands
import subprocess
import re

import os

from RenderToHTML import RenderToHTML

#
# GitPython
#
import git
from git import Repo

# Ingest the content of a JQL query (for all issues in a release) from a CSV file
class JiraExportQueryEntry:

# CSV Header:    
# Issue_Type,Issue_key,Issue_id,Parent_id,Summary,Resolution,Resolved,Closed_Date),ID,Assignee,Reporter,Priority,Created,Release_Note,Status,Fix_Version,Proposed_Release_Notes,Actual_Release_Note,

    def __init__(self, **kwargs):
        self.Issue_Type = kwargs.get('Issue Type')
        self.Issue_key = kwargs.get('Issue key')
        self.Issue_ID = kwargs.get('Issue id')
        self.Parent = kwargs.get('Parent id')
        self.Summary = kwargs.get('Summary')
        self.Resolution = kwargs.get('Resolution')
        self.Resolved = kwargs.get('Resolved')
        self.Closed_Date = kwargs.get('Custom field (Closed Date)')
        self.ID = kwargs.get('Custom field (ID)')
        self.Assignee = kwargs.get('Assignee')
        self.Reporter = kwargs.get('Reporter')
        self.Priority = kwargs.get('Priority')
        self.Created = kwargs.get('Created')
        self.Status = kwargs.get('Status')
        self.Fix_Version = kwargs.get('Fix Version/s')
        self.Proposed_Release_Note = kwargs.get('Custom field (Proposed Release Notes)')
        #self.Actual_Release_Note = kwargs.get('Actual_Release_Note')

    def __str__(self):
        return self.Issue_key + " " + self.Issue_Type + " " + self.Summary
    
# Ingest the content of consolidated Jira and Git information from a CSV file
class ConsolodatedDataImport:

# CSV Header:    
# Issue_Type,Issue_key,Issue_id,Parent_id,Summary,Resolution,Resolved,Closed_Date),ID,Assignee,Reporter,Priority,Created,Release_Note,Status,Fix_Version,Proposed_Release_Notes,Actual_Release_Note,

    def __init__(self, **kwargs):
        self.JiraId = kwargs.get('JiraId')
        self.InJira = kwargs.get('InJira')
        self.InGit = kwargs.get('InGit')
        self.JiraComment = kwargs.get('Jira Comment')
        self.GitComment = kwargs.get('Git Comment')
        self.ProposedReleaseNote = kwargs.get('ProposedReleaseNote')
        self.Take = kwargs.get('Take')
        self.ActualReleaseNote = kwargs.get('ActualReleaseNote')
        self.IssueType = kwargs.get('Issue Type')

    def __str__(self):
        return self.JiraId + " " + self.IssueType + " " + self.ActualReleaseNote    
    
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
# Dictionarys for Jira and Git to consolidate the two
#
jiraDictionary = {}
gitDictionary = {}
consolidatedDictionary = {}


class ConsolidatedEntry:

    def __init__(self, foundInJira, foundInGit, jiraComment, gitComment, proposed_release_note):
                 #, actual_release_note):
        self.foundInJira = foundInJira
        self.foundInGit = foundInGit
        self.jiraComment = jiraComment
        self.gitComment = gitComment
        self.proposed_release_note = proposed_release_note
        #self.actual_release_note = actual_release_note
 
    def __str__(self):
        return self.foundInJira + " " + self.foundInGit + " " + self.jiraComment + " " + self.gitComment + " " + self.proposed_release_note + " " # + self.actual_release_note
    
#
# Class to hold a git commit message of the form: <hash> <jira_id> <comment>
#
class gitCommitMessage:

    def __init__(self, hash, jiraId, comment):
        self.hash = hash
        self.jiraId = jiraId
        self.comment = comment
 
    def __str__(self):
        return "[" + self.hash + "],[" + self.jiraId + "],[" + self.comment + "]"


def main():

    #TODO: these need to be input as a parameter
    releaseNoteFile = "releaseNotes_for_25_1.csv"
    version = "25.1.1.21"
    previousVersion = "24.4.1.5"

    #
    # Input: A CSV file from a JQL query that is exported from Jira.
    #
    with open(releaseNoteFile, 'r') as inputCSVFile:
        csvReader = csv.DictReader(inputCSVFile)
        
        epicList = []
        defectList = []
        storyList = []
        spikeList = []
        subTaskList = []
        dependencyList = []
        supportList = []
        otherList = []

        for row in csvReader:
            entry = ConsolodatedDataImport(**row)

#            jiraDictionary[entry.Issue_key] = entry;

            match entry.IssueType:
                case "Defect": 
                    defectList.append(entry)
                case "Epic":
                    epicList.append(entry)
                case "Story":
                    storyList.append(entry)
                case "Sub-task":
                    subTaskList.append(entry)                    
                case "Dependency":
                    dependencyList.append(entry)    
                case "Support":
                    supportList.append(entry)                                      
                case "Spike":
                    spikeList.append(entry) 
                case _:
                    otherList.append(entry)

    # Render the content to a HTML file

    #TODO: pipe through the version info from the command line.    
    RenderToHTML("Output.html", version, previousVersion, False, epicList, storyList, defectList, supportList, otherList)

    # Retrieve the content of a git log between two tags
    #get_git_log("V25.1.0-alpha1", "V25.1.1.13")

    #read_and_parse_git_commit_line()

    #parse_csv_git_log()

''''
    #
    # Find all the issues that are listed in Jira, and cross reference these against the issues found in the Git commit(s)
    #
    for item in jiraDictionary:

        # Assume we can't find the entry in the git commit messages
        entry = ConsolidatedEntry("Yes", "No", jiraDictionary[item].Summary, "", jiraDictionary[item].Proposed_Release_Note)

        if item in gitDictionary:
            # If we find the issue in the GitDirectory mark it as found with the comment
            commitMessage = gitDictionary[item]

            entry.foundInGit = "Yes"
            entry.gitComment = commitMessage.comment

        consolidatedDictionary[item] = entry

    #
    # Find all the issues that are in Git, and determine if we found them in jira dictionary
    #         
    for item in gitDictionary:
        entry = ConsolidatedEntry("No", "Yes", "", gitDictionary[item].comment, "")#, "")

        print("Issues in Git", entry)

        #Entries that appear in both the gitDictionary and the jiraDictaion
        if item in jiraDictionary:
            entry.foundInJira = "Yes"
            entry.jiraComment = jiraDictionary[item].Summary
            entry.proposed_release_note = jiraDictionary[item].Proposed_Release_Note
            entry.actual_release_note = jiraDictionary[item].Actual_Release_Note

        consolidatedDictionary[item] = entry            

    # Write all the data to a CSV file with form <Jira_id>, <in_jira>, <in_git>, <jira summary>, <git comment>
    with open('consolidated_database.csv', 'w', newline='') as csvfile:
        commitWriter = csv.writer(csvfile, delimiter=',')
        commitWriter.writerow(['JiraId', 'InJira', 'InGit', 'Jira Comment', 'Git comment', 'ProposedReleaseNote', 'ActualReleaseNote'])

        for item in consolidatedDictionary:
            entry = consolidatedDictionary[item]

            #Write out the entry to the CSV file
            commitWriter.writerow([item, entry.foundInJira, entry.foundInGit, entry.jiraComment, entry.gitComment, entry.proposed_release_note, entry.actual_release_note]) 
'''


#
# Git schenanigans. This code will find the git commits between two tags
#

def get_git_log(source, destination):

    #Set the local folder to the PSS repo (hardcoded to my PSS repo)
    repoFolder = "/Users/rbg634/"
    repoDir = os.path.join(os.path.abspath(repoFolder), 'pss')

    #Set the repo
    repo = git.Repo(repoDir)

    #
    # Equivalent to: git log --oneline --nomerges $source..$dest
    #
    logs = repo.git.log("--oneline", "--no-merges", source + ".." + destination)
    lines = logs.splitlines()

    # Write the content of the commite messages into a CSV file of the form: <Hash>, <Jira_id>, <comment>
    with open('commitMessages.csv', 'w', newline='') as csvfile:
        commitWriter = csv.writer(csvfile, delimiter=',')
        commitWriter.writerow(['Hash', 'JiraId', 'Comment'])

        #Parse the git commit message to chunk into [hash, Jira number, comment]
        for line in lines:

            commitLine = parse_git_commit_line(line)

            print(commitLine)

            print("---------------------------------------------")

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
                
                commitMessage = gitCommitMessage(splittedString[0], splittedString[1], splittedString[2])
                commitWriter.writerow([commitMessage.hash, commitMessage.jiraId, commitMessage.comment])

                #Add the git commit entry into the git Dictionary, keyed on the Jira issue id
                gitDictionary[commitMessage.jiraId] = commitMessage
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


def parse_csv_git_log():

    #
    # Input: A CSV file from a JQL query that is exported from Jira.
    #
    with open('gitLogs_bp_to_18_Final.csv', 'r') as inputCSVFile:
        csvReader = csv.DictReader(inputCSVFile, delimiter=",")

        for row in csvReader:
            entry = GitCommitEntry(**row)
            gitDictionary[entry.jiraId] = entry;


def run_regex():
    regex = r"([a-f0-9]{6,8}) ([a-zA-Z0-9]+-[0-9]+)*.+"
    string = "aaaaaaa V500-1234 some message"
    match = re.findall(regex, string)  
    print(match)
        

if __name__ == "__main__":
    main()
