#
# From the git log messages between two tags, write out to a file
# a list of jira issues in a JQL query.
# This query can be used to tag the 'build version' field for each
# issue that was changed in this build
#

import argparse

from RenderToHTML import render_to_html
from ParseGitLog import get_git_log

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
    gitDictionary = get_git_log(repo_location, repo, source, dest)

    V500_issues = []
    VB400_issues = []
    V200_issues = []
    SDOCK_issues = []

    #
    # Find all the issues that are in Git
    #
    for item, entry in gitDictionary.items():

        if(item.startswith("V500")):
            V500_issues.append(entry)
        elif(item.startswith("VB400")):
            VB400_issues.append(entry)
        elif(item.startswith("SDOCK")):
            SDOCK_issues.append(entry)
        elif(item.startswith("V200")):
            V200_issues.append(entry)


    print("Rendering the JQL......")

    #Build the JQL query
    query = "issueKey in ("
    for item in V500_issues:
        query = query + item.jira_id + ","

    for item in VB400_issues:
        query = query + item.jira_id + ","

    for item in SDOCK_issues:
        query = query + item.jira_id + ","

    for item in V200_issues:
        query = query + item.jira_id + ","

    #Remove the trailing ','
    query = query[:-1]
    query = query + ")"

    print("JQL Query ", query)

    with open(output, "w") as jql_file:
        jql_file.write(query)

if __name__ == "__main__":
    main()

