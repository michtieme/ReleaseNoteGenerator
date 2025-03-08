from helpers import issue_key_to_hyperlink

def test_key_starts_with_unknown_no_hyperlink():
    assert issue_key_to_hyperlink("UNKNOWN") == "UNKNOWN"

def test_key_starts_with_AZMV_provides_AZDO_hyperlink():
    hyperlink = "<a href=\"https://dev.azure.com/MobileVideo/VideoManager/_workitems/edit/123\">AZMV-123</a>"
    assert issue_key_to_hyperlink("AZMV-123") == hyperlink

def test_key_starts_with_azmv_provides_AZDO_hyperlink():
    hyperlink = "<a href=\"https://dev.azure.com/MobileVideo/VideoManager/_workitems/edit/123\">azmv-123</a>"
    assert issue_key_to_hyperlink("azmv-123") == hyperlink

def test_key_starts_with_anything_else_provides_jira_hyperlink():
    hyperlink = "<a href=\"https://jira.mot-solutions.com/browse/ABC-123\">ABC-123</a>"
    assert issue_key_to_hyperlink("ABC-123") == hyperlink