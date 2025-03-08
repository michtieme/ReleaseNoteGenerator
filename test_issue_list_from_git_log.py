from issue_list_from_git_log import build_jql
from issue_list_from_git_log import parse_jira_issues_from_git_log

def test_build_jql_empty_list():
    assert build_jql([]) == "https://jira.mot-solutions.com/issues/?jql=issueKey in ()"

def test_build_jql_single_element():
    assert build_jql(['KEY-1']) == "https://jira.mot-solutions.com/issues/?jql=issueKey in (KEY-1)"

def test_build_jql_two_elemets():
    assert build_jql(['KEY-1', 'KEY-2']) == "https://jira.mot-solutions.com/issues/?jql=issueKey in (KEY-1,KEY-2)"

def test_build_jql_multi_elements():
    list = ['KEY-1','KEY-2','KEY-3']
    assert build_jql(list) == "https://jira.mot-solutions.com/issues/?jql=issueKey in (KEY-1,KEY-2,KEY-3)"

def test_build_jql_duplicate_elements_are_removed():
    duplicate_key = 'KEY-1'
    list = [duplicate_key, duplicate_key]
    assert parse_jira_issues_from_git_log(list, []) == "https://jira.mot-solutions.com/issues/?jql=issueKey in (KEY-1)"

def test_build_jql_unknown_elements_are_removed():
    list = ['KEY-1', 'UNKNOWN']
    blacklist = ['UNKNOWN']
    assert parse_jira_issues_from_git_log(list, blacklist) == "https://jira.mot-solutions.com/issues/?jql=issueKey in (KEY-1)"
