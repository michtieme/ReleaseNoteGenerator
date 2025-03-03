"""Engineering Release Note Generator - pretty prints the content of a git log to html"""

import argparse
import dataclasses

from RenderToHTML import render_to_html
from ParseGitLog import get_git_log

from NoteType import ReleaseNoteType

@dataclasses.dataclass
class ConsolidatedEntry:

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
    """Pretty print the content of a git log to html"""
    #
    #Parse the command line arguments
    #
    parser = argparse.ArgumentParser()
    parser.add_argument('-j','--jira', type=str, help='Location of a CSV file that was exported from a Jira Query', required=True)
    parser.add_argument('-l','--repo_loc', type=str, help='Location of a git repo to search history in', required=True)
    parser.add_argument('-r','--repo', type=str, help='The name of the git repo in which to search the history', required=True)
    parser.add_argument('-s','--source', type=str, help='Git tag of starting range to search in git', required=True)
    parser.add_argument('-d','--dest', type=str, help='Git tag of destination to search in git', required=True)
    parser.add_argument('-o','--output', type=str, help='HTML to render output to', required=True)

    args = parser.parse_args()
    arguments = vars(args)

    source = arguments['source']
    destination = arguments['dest']
    repo_location = arguments['repo_loc']
    repo = arguments['repo']
    output = arguments['output']

    #Fetch the content of a parsed git log
    gitDictionary = get_git_log(repo_location, repo, source, destination)

    epics = []
    defects = []
    stories = []
    support_issues = []
    other = []

    #
    # Find all the issues that are in Git
    #
    for item, dict_entry in gitDictionary.items():
        entry = ConsolidatedEntry(item, "No", "Yes", "", "", dict_entry.comment, "")
        defects.append(entry)

    # Render the content to a HTML file
    render_to_html(output, destination, source, epics, stories, defects, support_issues, other, ReleaseNoteType.ENGINEERING_NOTE)

if __name__ == "__main__":
    main()
