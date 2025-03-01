#
# From the git log messages between two tags, write out to a file
# a list of jira issues in a JQL query.
# This query can be used to tag the 'build version' field for each
# issue that was changed in this build
#

import argparse

from RenderToHTML import RenderToHTML
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
    argsDict = vars(args)

    sourceTag = argsDict['source']
    destTag = argsDict['dest']
    repoLocation = argsDict['repo_loc']
    repo = argsDict['repo']
    outputFile = argsDict['output']

    #Fetch the content of a parsed git log
    gitDictionary = get_git_log(repoLocation, repo, sourceTag, destTag)

    V500List = []
    VB400List = []    
    V200List = []
    SDOCKList = []

    #
    # Find all the issues that are in Git
    #         
    for item in gitDictionary:

        if(item.startswith("V500")):
            V500List.append(gitDictionary[item])
        elif(item.startswith("VB400")):
            VB400List.append(gitDictionary[item])
        elif(item.startswith("SDOCK")):
            SDOCKList.append(gitDictionary[item])
        elif(item.startswith("V200")):
            V200List.append(gitDictionary[item])
            

    #Build the JQL query
    jqlQuery = "issueKey in ("
    for item in V500List:
        jqlQuery = jqlQuery + item.jiraId + ","

    for item in VB400List:
        jqlQuery = jqlQuery + item.jiraId + ","

    for item in SDOCKList:
        jqlQuery = jqlQuery + item.jiraId + ","

    for item in V200List:
        jqlQuery = jqlQuery + item.jiraId + ","        

    #Remove the trailing ','
    jqlQuery = jqlQuery[:-1]
    jqlQuery = jqlQuery + ")"
    
    print("JQL Query ", jqlQuery)

    with open(outputFile, "w") as jqlFile:
        jqlFile.write(jqlQuery)    

if __name__ == "__main__":
    main() 

