"""Release Note Generator - pull the git and jira data together to provide data for review,
   and create release notes"""

import csv
import argparse
import dataclasses

from render_to_html import render_to_html
from parse_git_log import get_git_log

from NoteType import ReleaseNoteType

@dataclasses.dataclass
class JiraExportQueryEntry:
    """Class to Ingest the content of a JQL query (for all issues in a release) from a CSV file"""

# CSV Header:
#Issue Type^Issue key^Issue id^Parent id^Summary^Resolution^Resolved^Custom field (Closed Date)^Custom field (ID)^Assignee^Reporter^Priority^Created^Status^Fix Version/s^Custom field (Proposed Release Notes)
#Note this CSV export uses the '^' delimiter to avoid having to worry about handling ',' in comment fields

    def __init__(self, **kwargs):
        self.issue_type = kwargs.get('Issue Type')
        self.issue_key = kwargs.get('Issue key')
        self.issue_id = kwargs.get('Issue id')
        self.parent = kwargs.get('Parent id')
        self.summary = kwargs.get('Summary')
        self.resolution = kwargs.get('Resolution')
        self.resolved = kwargs.get('Resolved')
        self.closed_date = kwargs.get('Custom field (Closed Date)')
        self.id = kwargs.get('Custom field (ID)')
        self.assignee = kwargs.get('Assignee')
        self.reporter = kwargs.get('Reporter')
        self.priority = kwargs.get('Priority')
        self.created = kwargs.get('Created')
        self.status = kwargs.get('Status')
        self.fix_version = kwargs.get('Fix Version/s')
        self.proposed_release_note = kwargs.get('Custom field (Proposed Release Notes)')

    def __str__(self):
        return self.issue_key + " " + self.issue_type + " " + self.summary

@dataclasses.dataclass
class ReleaseNoteDataImport:
    """Class to Import the modified content of the release notes for converting to HTML"""
# CSV Header:
# Issue_Type,Issue_key,Issue_id,Parent_id,Summary,Resolution,Resolved,Closed_Date),ID,Assignee,Reporter,Priority,Created,Release_Note,Status,Fix_Version,Proposed_Release_Notes,Actual_Release_Note,

    def __init__(self, **kwargs):
        self.jira_id = kwargs.get('JiraId')
        self.issue_type = kwargs.get('IssueType')
        self.in_jira = kwargs.get('InJira')
        self.in_git = kwargs.get('InGit')
        self.jira_comment = kwargs.get('Jira Comment')
        self.git_comment = kwargs.get('Git Comment')
        self.proposed_release_note = kwargs.get('ProposedReleaseNote')
        self.take = kwargs.get('Take')
        self.actual_release_note = kwargs.get('ActualReleaseNote')

    def __str__(self):
        return self.jira_id + " " + self.issue_type + " " + self.jira_comment + " " + self.actual_release_note

@dataclasses.dataclass
class ConsolidatedEntry:
    """Class to represent data that is consolidated between git and jira"""
    def __init__(self, jira_id, found_in_jira, found_in_git, jira_comment, issue_type, git_comment, release_note):
        self.jira_id = jira_id
        self.found_in_jira = found_in_jira
        self.found_in_git = found_in_git
        self.jira_comment = jira_comment
        self.issue_type = issue_type
        self.git_comment = git_comment
        self.release_note = release_note

    def __str__(self):
        return self.found_in_jira + " " + self.found_in_git + " " + self.jira_comment + " " + self.issue_type + " " + self.git_comment + " " + self.release_note

def main():
    """pull git and jira data together to provide data for review, and to create release notes"""

    #
    #Parse the command line arguments
    #
    parser = argparse.ArgumentParser()
    parser.add_argument('-j','--jira', type=str, help='Location of a CSV file that was exported from a Jira Query', required=True)
    parser.add_argument('-l','--repo_loc', type=str, help='Location of a git repo to search history in', required=True)
    parser.add_argument('-r','--repo', type=str, help='The name of the git repo in which to search the history', required=True)
    parser.add_argument('-s','--source', type=str, help='Git tag of starting range to search in git', required=True)
    parser.add_argument('-d','--dest', type=str, help='Git tag of destination to search in git', required=True)
    parser.add_argument('-i','--input', type=str, help='Location of sanitised release notes to be render to HTML. This is a CSV file imported from Google Sheets.', required=True)
    parser.add_argument('-v','--review', type=str, help='CSV file of data to be reviewed for release note content', required=True)
    parser.add_argument('-o','--output', type=str, help='HTML to render output to', required=True)

    args = parser.parse_args()
    arguments = vars(args)

    jira_export_file = arguments['jira']
    source = arguments['source']
    dest = arguments['dest']
    repo_location = arguments['repo_loc']
    repo = arguments['repo']
    output_file = arguments['output']
    sanitised_release_notes = arguments['input']
    csv_file_for_review = arguments['review']

    jira_dictionary = {}
    consolidated_dictionary = {}

    #
    # import the data from a JQL query that has been exported from Jira to a CSV
    #
    with open(jira_export_file, 'r', encoding="utf-8") as input_csv_file:

        csv_reader = csv.DictReader(input_csv_file, delimiter="^")

        #TODO: Handle errors reading the CSV
        #

        for row in csv_reader:
            entry = JiraExportQueryEntry(**row)
            jira_dictionary[entry.issue_key] = entry

    #Fetch the content of a parsed git log
    git_dictionary, git_log_command, git_log = get_git_log(repo_location, repo, source, dest)

    #
    # Find all the issues that are listed in Jira, and cross reference these against the issues found in the Git commit(s)
    #
    for item, entry in jira_dictionary.items():

        # Assume we can't find the entry in the git commit messages
        entry = ConsolidatedEntry(item, "Yes", "No", entry.summary, entry.issue_type, "", entry.proposed_release_note)

        if item in git_dictionary:
            # If we find the issue in the GitDirectory mark it as found with the comment
            commit_message = git_dictionary[item]

            entry.found_in_git = "Yes"
            entry.git_comment = commit_message

        consolidated_dictionary[item] = entry

    #
    # Find all the issues that are in Git, and determine if we found them in jira dictionary
    #
    for item, entry in git_dictionary.items():

        #Add each commit entry found by the key as a unique entry in the html table
        for commit_messages in entry:

            new_item = ConsolidatedEntry(item, "No", "Yes", "", "", commit_messages.comment, "")

            #Entries that appear in both the gitDictionary and the jiraDictaion
            if item in jira_dictionary:
                new_item.found_in_jira = "Yes"
                new_item.jira_comment = jira_dictionary[item].summary
                new_item.issue_type = jira_dictionary[item].issue_type
                new_item.release_note = jira_dictionary[item].proposed_release_note

            consolidated_dictionary[item] = new_item

    # Write all the consolidated data to a CSV file. This forms the basis of the release notes for review
    with open(csv_file_for_review, 'w', encoding="utf-8", newline='') as csvfile:
        commit_writer = csv.writer(csvfile, delimiter=',')
        commit_writer.writerow(['JiraId', 'IssueType', 'InJira', 'InGit', 'Jira Comment', 'Git comment', 'ProposedReleaseNote'])

        for item, entry in consolidated_dictionary.items():
            comments = ''
            #Write out the entry to the CSV file
            for comment in entry.git_comment:
                comments += comment + '\n'
            commit_writer.writerow([item, entry.issue_type, entry.found_in_jira, entry.found_in_git, entry.jira_comment, comments, entry.release_note])

    #
    # Read in the sanitised CSV file that has been exported from a Google Sheet. This determines what is rendered to HTML
    #
    epics = []
    defects = []
    stories = []
    spikes = []
    subtasks = []
    dependencies = []
    support_issues = []
    other = []

    with open(sanitised_release_notes, 'r', encoding="utf-8") as exported_csv_file:
        csv_reader = csv.DictReader(exported_csv_file, delimiter="\t")

        #TODO handle errors when reading the CSV file

        for row in csv_reader:

            entry = ReleaseNoteDataImport(**row)

            if entry.take == "Yes":
                consolidated_entry = ConsolidatedEntry(entry.jira_id,
                                                      entry.in_jira,
                                                      entry.in_git,
                                                      entry.jira_comment,
                                                      entry.issue_type,
                                                      entry.git_comment,
                                                      entry.actual_release_note)

                match entry.issue_type:
                    case "Defect":
                        defects.append(consolidated_entry)
                    case "Epic":
                        epics.append(consolidated_entry)
                    case "Story":
                        stories.append(consolidated_entry)
                    case "Sub-task":
                        subtasks.append(consolidated_entry)
                    case "Dependency":
                        dependencies.append(consolidated_entry)
                    case "Support":
                        support_issues.append(consolidated_entry)
                    case "Spike":
                        spikes.append(consolidated_entry)
                    case _:
                        other.append(consolidated_entry)

    # Render the content to a HTML file
    render_to_html(output_file, dest, source, epics, stories, defects, support_issues, other, ReleaseNoteType.RELEASE_NOTE)

if __name__ == "__main__":
    main()
