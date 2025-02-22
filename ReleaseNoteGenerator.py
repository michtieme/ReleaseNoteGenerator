import csv

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
    
class ConsolidatedEntry:

    def __init__(self, foundInJira, foundInGit, jiraComment, gitComment, proposed_release_note):
        self.foundInJira = foundInJira
        self.foundInGit = foundInGit
        self.jiraComment = jiraComment
        self.gitComment = gitComment
        self.proposed_release_note = proposed_release_note
 
    def __str__(self):
        return self.foundInJira + " " + self.foundInGit + " " + self.jiraComment + " " + self.gitComment + " " + self.proposed_release_note

def main():

    #TODO: these need to be input as a parameter
    jiraExportFile = "ExportedFromJira.csv"
    version = "25.1.1.21"
    previousVersion = "24.4.1.5"

    jiraDictionary = {}
    consolidatedDictionary = {}    

    #
    # Input: A CSV file from a JQL query that is exported from Jira.
    #
    with open(jiraExportFile, 'r') as inputCSVFile:
        csvReader = csv.DictReader(inputCSVFile, delimiter="^")

        #TODO: Handle errors reading the CSV
        
        epicList = []
        defectList = []
        storyList = []
        spikeList = []
        subTaskList = []
        dependencyList = []
        supportList = []
        otherList = []

        for row in csvReader:
            entry = JiraExportQueryEntry(**row)

            jiraDictionary[entry.IssueId] = entry

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

    #Fetch the content of the git log
    gitDictionary = get_git_log("/Users/rbg634/", "pss", "V25.1.0-alpha1", "V25.1.1.13")
 
    #
    # Find all the issues that are listed in Jira, and cross reference these against the issues found in the Git commit(s)
    #
    for item in jiraDictionary:

        # Assume we can't find the entry in the git commit messages
        entry = ConsolidatedEntry("Yes", "No", jiraDictionary[item].Summary, "", jiraDictionary[item].ProposedReleaseNote)

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
        entry = ConsolidatedEntry("No", "Yes", "", gitDictionary[item].comment, "")

        print("Issues in Git", entry)

        #Entries that appear in both the gitDictionary and the jiraDictaion
        if item in jiraDictionary:
            entry.foundInJira = "Yes"
            entry.jiraComment = jiraDictionary[item].Summary
            entry.proposed_release_note = jiraDictionary[item].ProposedReleaseNote

        consolidatedDictionary[item] = entry            

    # Write all the consolidated data to a CSV file with form <Jira_id>, <in_jira>, <in_git>, <jira summary>, <git comment>
    with open('consolidated_database.csv', 'w', newline='') as csvfile:
        commitWriter = csv.writer(csvfile, delimiter=',')
        commitWriter.writerow(['JiraId', 'InJira', 'InGit', 'Jira Comment', 'Git comment', 'ProposedReleaseNote'])

        for item in consolidatedDictionary:
            entry = consolidatedDictionary[item]

            #Write out the entry to the CSV file
            commitWriter.writerow([item, entry.foundInJira, entry.foundInGit, entry.jiraComment, entry.gitComment, entry.proposed_release_note]) 


    # Render the content to a HTML file

    #TODO: pipe through the version info from the command line.    
    #RenderToHTML("Output.html", version, previousVersion, False, epicList, storyList, defectList, supportList, otherList)            

if __name__ == "__main__":
    main() 

