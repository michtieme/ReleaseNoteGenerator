"""
 From the git log messages between two tags,
 find a list of jira issues and wrap them up into a JQL query that can be opened in Jira.
 This query can be used to tag the 'build version' field for each
 issue that was changed in this build
"""

import argparse
import webbrowser

from parse_git_log import get_git_log

def main():

    #
    #Parse the command line arguments
    #
    parser = argparse.ArgumentParser()
    parser.add_argument('-l','--repo_loc', type=str, help='Location of a git repo to search history in', required=True)
    parser.add_argument('-r','--repo', type=str, help='The name of the git repo in which to search the history', required=True)
    parser.add_argument('-s','--source', type=str, help='Git tag of starting range to search in git', required=True)
    parser.add_argument('-d','--dest', type=str, help='Git tag of destination to search in git', required=True)
    parser.add_argument('-o','--output', type=str, help='JQL output for issues that have changed', required=True)

    args = parser.parse_args()
    arguments = vars(args)

    source = arguments['source']
    dest = arguments['dest']
    repo_location = arguments['repo_loc']
    repo = arguments['repo']
    output = arguments['output']

    #Fetch the content of a parsed git log
    git_dictionary, git_log_command, git_log = get_git_log(repo_location, repo, source, dest)

    azdo_projects = ['AZMV', 'AMZV']
    jql_url = parse_jira_issues_from_git_log(git_dictionary.keys(), azdo_projects)

    #Write the JQL query to an output file
    with open(output, "w") as jql_file:
        jql_file.write(jql_url)

    #Open a browser with to view the content of the JQL query
    webbrowser.open(jql_url, new=1)

def parse_jira_issues_from_git_log(keys, blacklist):
    """Parse a list of jira issues from a git log, ignoring blacklisted project keys"""
    blacklisted_issues = []
    jira_issues = []

    #
    # Find all the unique issues by key. Ignore 'UNKOWN' keys and blacklisted projects
    #
    for item in keys:
        jira_issue = True

        for project in blacklist:
            if item.upper().startswith("UNKNOWN"):
                jira_issue = False
                break
            elif item.upper().startswith(project):
                if item not in blacklisted_issues:
                    blacklisted_issues.append(item)
                jira_issue = False
                break

        if(jira_issue and item not in jira_issues):
            jira_issues.append(item)

    return build_jql(jira_issues)

def build_jql(jira_issues):
    """Build a JQL string to access Jira for a set of issues"""
    return "https://jira.mot-solutions.com/issues/?jql=" + build_jira_query(jira_issues)

def build_jira_query(issues):
    """Build a JQL query string for a set of issues, ignoring duplicates"""
    #Build the JQL query
    query = "issueKey in ("
    for item in issues:
        query += item + ","

    #Remove the trailing ',' (as long as the list is not empty)
    if issues:
        query = query[:-1]

    query += ")"

    return query

if __name__ == "__main__":
    main()

