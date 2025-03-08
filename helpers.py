"""Helper functions"""

def issue_key_to_hyperlink(issue):
    """convert an issue id string to a hyperlink (either jira or AZDO)"""
    #Render hyperlinks
    dash_location = -1
    url = ""

    if issue.startswith("UNKNOWN"):
        return issue

    # AZMV issues are in AZDO
    if issue.startswith(("AZMV", "azmv")):

        dash_location = issue.find('-')
        length = len(issue)

        if dash_location != -1:
            azdo_id = issue[dash_location+1:length]
            url = 'https://dev.azure.com/MobileVideo/VideoManager/_workitems/edit/' + azdo_id

    else:
        # Assume the issue is a Jira instead
        url = "https://jira.mot-solutions.com/browse/" + issue

    return '<a href="' + url + '">' + issue + '</a>'
