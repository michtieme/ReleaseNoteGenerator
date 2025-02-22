import csv
import argparse

from RenderToHTML import RenderToHTML
from ParseGitLog import get_git_log


# Ingest the content of a JQL query (for all issues in a release) from a CSV file
class JiraExportQueryEntry:

# CSV Header:    
#Issue Type^Issue key^Issue id^Parent id^Summary^Resolution^Resolved^Custom field (Closed Date)^Custom field (ID)^Assignee^Reporter^Priority^Created^Status^Fix Version/s^Custom field (Proposed Release Notes)
#Note this CSV export uses the '^' delimiter to avoid having to worry about handling ',' in comment fields

    def __init__(self, **kwargs):
        self.IssueType = kwargs.get('Issue Type')
        self.IssueKey = kwargs.get('Issue key')
        self.IssueId = kwargs.get('Issue id')
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
        self.FixVersion = kwargs.get('Fix Version/s')
        self.ProposedReleaseNote = kwargs.get('Custom field (Proposed Release Notes)')

    def __str__(self):
        return self.IssueKey + " " + self.IssueType + " " + self.Summary
    
# Import the modified content of the release notes for converting to HTML
class ReleaseNoteDataImport:

# CSV Header:    
# Issue_Type,Issue_key,Issue_id,Parent_id,Summary,Resolution,Resolved,Closed_Date),ID,Assignee,Reporter,Priority,Created,Release_Note,Status,Fix_Version,Proposed_Release_Notes,Actual_Release_Note,

    def __init__(self, **kwargs):
        self.JiraId = kwargs.get('JiraId')
        self.IssueType = kwargs.get('IssueType')        
        self.InJira = kwargs.get('InJira')
        self.InGit = kwargs.get('InGit')
        self.JiraComment = kwargs.get('Jira Comment')
        self.GitComment = kwargs.get('Git Comment')
        self.ProposedReleaseNote = kwargs.get('ProposedReleaseNote')
        self.Take = kwargs.get('Take')
        self.ActualReleaseNote = kwargs.get('ActualReleaseNote')

    def __str__(self):
        return self.JiraId + " " + self.IssueType + " " + self.JiraComment + " " + self.ActualReleaseNote    
        
    
class ConsolidatedEntry:

    def __init__(self, foundInJira, foundInGit, jiraComment, issueType, gitComment, proposed_release_note):
        self.foundInJira = foundInJira
        self.foundInGit = foundInGit
        self.jiraComment = jiraComment
        self.issueType = issueType
        self.gitComment = gitComment
        self.proposed_release_note = proposed_release_note
 
    def __str__(self):
        return self.foundInJira + " " + self.foundInGit + " " + self.jiraComment + " " + self.issueType + " " + self.gitComment + " " + self.proposed_release_note

def main():

    #
    #Parse the command line arguments
    #
    parser = argparse.ArgumentParser()
    parser.add_argument('-j','--jira', type=str, help='Location of a CSV file that was exported from a Jira Query', required=True)
    parser.add_argument('-l','--repo_loc', type=str, help='Location of a git repo to search history in', required=True)
    parser.add_argument('-r','--repo', type=str, help='The name of the git repo in which to search the history', required=True)
    parser.add_argument('-s','--source', type=str, help='Git tag of starting range to search in git', required=True)
    parser.add_argument('-d','--dest', type=str, help='Git tag of destination to search in git', required=True)

    args = parser.parse_args()
    argsDict = vars(args)

    jiraExportFile = argsDict['jira']
    sourceTag = argsDict['source']
    destTag = argsDict['dest']
    repoLocation = argsDict['repo_loc']
    repo = argsDict['repo']

    jiraDictionary = {}
    consolidatedDictionary = {}    

    #
    # import the data from a JQL query that has been exported from Jira to a CSV
    #
    with open(jiraExportFile, 'r') as inputCSVFile:

        csvReader = csv.DictReader(inputCSVFile, delimiter="^")

        #TODO: Handle errors reading the CSV
        #         

        for row in csvReader:        
            entry = JiraExportQueryEntry(**row)
            jiraDictionary[entry.IssueKey] = entry

    #Fetch the content of a parsed git log
    gitDictionary = get_git_log(repoLocation, repo, sourceTag, destTag)
 
    #
    # Find all the issues that are listed in Jira, and cross reference these against the issues found in the Git commit(s)
    #
    for item in jiraDictionary:

        # Assume we can't find the entry in the git commit messages
        entry = ConsolidatedEntry("Yes", "No", jiraDictionary[item].Summary, jiraDictionary[item].IssueType, "", jiraDictionary[item].ProposedReleaseNote)

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
        entry = ConsolidatedEntry("No", "Yes", "", "", gitDictionary[item].comment, "")

        print("Issues in Git", entry)

        #Entries that appear in both the gitDictionary and the jiraDictaion
        if item in jiraDictionary:
            entry.foundInJira = "Yes"
            entry.jiraComment = jiraDictionary[item].Summary
            entry.issueType = jiraDictionary[item].IssueType
            entry.proposed_release_note = jiraDictionary[item].ProposedReleaseNote

        consolidatedDictionary[item] = entry            

    # Write all the consolidated data to a CSV file. This forms the basis of the release notes for review
    with open('consolidated_database.csv', 'w', newline='') as csvfile:
        commitWriter = csv.writer(csvfile, delimiter=',')
        commitWriter.writerow(['JiraId', 'IssueType', 'InJira', 'InGit', 'Jira Comment', 'Git comment', 'ProposedReleaseNote'])

        for item in consolidatedDictionary:
            entry = consolidatedDictionary[item]

            #Write out the entry to the CSV file
            commitWriter.writerow([item, entry.issueType, entry.foundInJira, entry.foundInGit, entry.jiraComment, entry.gitComment, entry.proposed_release_note]) 

    #
    # Read in the sanitised CSV file that has been exported from a Google Sheet. This determines what is rendered to HTML
    #
    releaseNotes= "ImportedFromGoogleSheets.csv"

    epicList = []
    defectList = []
    storyList = []
    spikeList = []
    subTaskList = []
    dependencyList = []
    supportList = []
    otherList = []

    with open(releaseNotes, 'r') as exportedCSVFile:
        csvReader = csv.DictReader(exportedCSVFile, delimiter="^")

        #TODO handle errors when reading the CSV file

        for row in csvReader:

            print(row)
            entry = ReleaseNoteDataImport(**row)

            print(entry)

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
    RenderToHTML("Output.html", destTag, sourceTag, False, epicList, storyList, defectList, supportList, otherList)            

if __name__ == "__main__":
    main() 

