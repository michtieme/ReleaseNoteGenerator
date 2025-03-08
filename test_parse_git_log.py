from ParseGitLog import trim_excess_prefix_characters
from ParseGitLog import split_commit_message
from ParseGitLog import GitCommitMessage

def test_trim_single_comma():
    assert trim_excess_prefix_characters(",abcdef") == "abcdef"

def test_trim_multi_comma():
    assert trim_excess_prefix_characters(",,,,abcdef") == "abcdef"

def test_trim_single_colon():
    assert trim_excess_prefix_characters(":abcdef") == "abcdef"

def test_trim_multi_colon():
    assert trim_excess_prefix_characters("::::abcdef") == "abcdef"

def test_trim_single_hyphen():
    assert trim_excess_prefix_characters("-abcdef") == "abcdef"

def test_trim_multi_hyphen():
    assert trim_excess_prefix_characters("----abcdef") == "abcdef"

def test_commit_message_contains_sha_jira_message():
    log = split_commit_message("abcd123 ABC-123 My fancy message")
    assert(log.hash == "abcd123")
    assert(log.jira_id == "ABC-123")
    assert(log.comment == "My fancy message")

def test_commit_message_contains_sha_jira_message_and_excess_characters_removed():
    log = split_commit_message("abcd123 ABC-123 ,:-My fancy message")
    assert(log.hash == "abcd123")
    assert(log.jira_id == "ABC-123")
    assert(log.comment == "My fancy message")

def test_commit_message_contains_sha_jira_message_and_only_matches_first_jira():
    log = split_commit_message("abcd123 ABC-123 My fancy message ABC-456")
    assert(log.hash == "abcd123")
    assert(log.jira_id == "ABC-123")
    assert(log.comment == "My fancy message ABC-456")

def test_commit_message_contains_sha_jira_message_and_can_fix_malformed_jira_ids():
    log = split_commit_message("abcd123 ABC:123 My fancy message")
    assert(log.hash == "abcd123")
    assert(log.jira_id == "ABC-123")
    assert(log.comment == "My fancy message")

#TODO: Fix this Failing test. The regex is matching the second jira id, not the first
#      This is conflicting with 'test_commit_message_punctuation_between_jira_and_commit_message'
#      which is matching this regex = r"([\s]([a-zA-Z0-9]+-[0-9]+)[\s](.+))" (note [\s])
#
#def test_commit_message_contains_sha_jira_message_and_can_fix_malformed_jira_ids_dont_match_second_jira_id():
#    log = split_commit_message("abcd123 ABC:123 My fancy message ABC-456")
#    assert(log.hash == "abcd123")
#    assert(log.jira_id == "ABC-123")
#    assert(log.comment == "My fancy message ABC-456")

def test_commit_message_could_not_find_sha_in_git_log():
    log = split_commit_message("my_entry_that_is_not_a_hash ABC-123 My fancy message")
    assert(log.hash == "")
    assert(log.jira_id == "UNKNOWN")
    assert(log.comment == "my_entry_that_is_not_a_hash ABC-123 My fancy message")

def test_commit_message_could_not_find_jira_in_git_log():
    log = split_commit_message("abcd123 ABC123 My fancy message")
    assert(log.hash == "abcd123")
    assert(log.jira_id == "UNKNOWN")
    assert(log.comment == "ABC123 My fancy message")

def test_commit_message_punctuation_between_jira_and_commit_message():
    log = split_commit_message("abcd123 ABC-123:My fancy message")
    assert(log.hash == "abcd123")
    assert(log.jira_id == "ABC-123") #TODO: Should handle this case to parse the punctuation
    assert(log.comment == "My fancy message")

