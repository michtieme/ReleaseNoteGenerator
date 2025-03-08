"""Render the content of various lists to a predefined HTML format
 <Header>
 <List of Epics>
 <List of Stories>
 <list of Defects>
 <list of Support issues>
"""

from NoteType import ReleaseNoteType
from helpers import issue_key_to_hyperlink

def render_to_html(output_location, version, previous_version, commits):
    """Render the content of a commit list into a html file."""

    epics = []
    defects = []
    stories = []
    spikes = []
    subtasks = []
    dependencies = []
    support_issues = []
    other = []

    for entry in commits:
        match entry.issue_type:
            case "Defect":
                defects.append(entry)
            case "Epic":
                epics.append(entry)
            case "Story":
                stories.append(entry)
            case "Sub-task":
                subtasks.append(entry)
            case "Dependency":
                dependencies.append(entry)
            case "Support":
                support_issues.append(entry)
            case "Spike":
                spikes.append(entry)
            case _:
                other.append(entry)

    with open(output_location, "w") as output_html:

        render_header(output_html)

        render_body(output_html, version, previous_version, ReleaseNoteType.RELEASE_NOTE)
        render_epics(output_html, epics, ReleaseNoteType.RELEASE_NOTE)
        render_stories(output_html, stories, "Minor enhancements made to device software", ReleaseNoteType.RELEASE_NOTE)
        render_defects(output_html, defects, "Defects resolved in device software", ReleaseNoteType.RELEASE_NOTE)
        render_support(output_html, support_issues, "Customer support issues resolved in device software", ReleaseNoteType.RELEASE_NOTE)

        #Render issues that are not suitable for release notes
        render_horizontal_line(output_html)

        render_close_body(output_html)

    output_html.close()

def render_engineering_notes(output_location, version, previous_version, issues, git_log_command, git_log, jql):
    """Render the content of engineering notes into a html file."""

    with open(output_location, "w") as output_html:

        render_header(output_html)

        render_body(output_html, version, previous_version, ReleaseNoteType.ENGINEERING_NOTE)
        render_table_of_issues(output_html, issues, "Issues modified in this release", ReleaseNoteType.ENGINEERING_NOTE)

        # Render the git log
        render_horizontal_line(output_html)
        render_git_log(output_html, git_log_command, git_log)

        # Render the JQL
        render_horizontal_line(output_html)
        render_jql(jql, output_html)

        render_close_body(output_html)

    output_html.close()

def render_release_notes(output_location, version, previous_version, epics, stories, defects, support_issues, other, note_type):
    """Render the content of various lists into a html file."""

    with open(output_location, "w") as output_html:

        render_header(output_html)

        render_body(output_html, version, previous_version, note_type)
        render_epics(output_html, epics, note_type)
        render_stories(output_html, stories, "Minor enhancements made to device software", note_type)
        render_defects(output_html, defects, "Defects resolved in device software", note_type)
        render_support(output_html, support_issues, "Customer support issues resolved in device software", note_type)

        #Render issues that are not suitable for release notes
        render_horizontal_line(output_html)

        render_close_body(output_html)

    output_html.close()


def render_horizontal_line(output):
    """Render a horizontal line to the html"""
    output.write("\n\t\t\t\t<hr>\n")

def render_git_log(output, git_log_command, git_log):
    """Render the content of the git log string"""
    tabs = '\t\t\t\t'
    html = tabs + "<dt>Git Log</dt>\n" + tabs + "<br>\n" + tabs + git_log_command
    formatted_git_log = tabs + "<pre>\n"

    lines = git_log.split(sep='\n')
    for line in lines:
        formatted_git_log += line + "\n"

    formatted_git_log += tabs + "</pre>"

    html += formatted_git_log

    output.write(html)

def render_jql(jira_url, output):
    """Render the content of a JQL query to html"""

    tabs = '\t\t\t\t'
    html = tabs + '<dt>Jira</dt>\n' + tabs + '<br>\n'
    jira_hyperlink = '<a href="' + jira_url + '">' + 'Jira</a>\n'
    html += 'Display the changed issues in ' + jira_hyperlink

    output.write(html)

def render_header(output):
    """Render the html header"""

    # Write the HTML Header

    #TODO: update the title

    #TODO: Set the release notes title correctly
    html = """<html lang="en">
        <head>
            <meta charset="utf-8"/>
            <style>
                div.releaseNotes dt {
                    font-family: sans-serif;
                    font-weight: bold;
                }
                div.releaseNotes dd {
                    padding: 0px 0px 10px 0px;
                }
                div.releaseNotes table {
                border-collapse: collapse;
                }
                div.releaseNotes table.issues tr:nth-child(even) {
                    background-color: #f2f2f2;
                }
                div.releaseNotes td, div.releaseNotes th {
                border: 4px solid transparent;
                padding: 0px;
                text-align: left;
                }
                div.releaseNotes table.table-border td, div.releaseNotes table.table-border th {
                border: 1px solid black;
                padding: 4px;
                }
                div.releaseNotes .issueid {
                width: 140px
                }
                div.releaseNotes .configsetting {
                width: 240px
                }
            </style>

            <title>Release Notes - V500 - Version V500_25.1</title>
        </head>"""

    #TODO: should pipe through the release notes version in the <title>

    output.write(html)

def render_body(html, version, previous_version, note_type):
    """Render the body of the html"""

    # Write the HTML Body text

    html_body = """
    <body>
        <div class="releaseNotes">
            <h1>Motorola Solutions release notes - """

    next = "</h1>" + """
            <!--<p><em>Warning:</em> These release notes are incomplete, expect an update</p>-->
            <h2>Changes</h2>
            <hr>"""

    software_version = "<h3>Software updated in " + version + "</h3>"

    tail = """
            <ul>
                <li>V500 firmware
                <li>VB400 firmware
                <!--<li>VT50 / VT100 firmware-->
                <li>DockController firmware
                <li>Smart Dock firmware
            </ul>"""

    since = "<h3>Changes since " + previous_version + "</h3>" + """
            <dl>\n"""

    if note_type == note_type.RELEASE_NOTE:
        content = html_body + next + software_version + tail + since
    else:
        content = html_body + next + software_version + since

    html.write(content)

def render_close_body(output_html):
    """Render the closing tags of the html"""
    # Write the HTML body closing tags

    closing_braces = "</body>"

    then = """
            <dl>
        </div>\n"""

    output_html.write(then + closing_braces)

def render_table_of_issues(output_html, issues, header, note_type):
    """Render the content of a table of issues to html"""

    tabs = '\t\t\t\t'

    # Render a table of issues
    output_html.write(tabs + "<dt>" + header + "</dt>")
    output = """
                <dd>
                    <table class="issues">
                        <colgroup>
                            <col class="issueid">
                            <col>
                        </colgroup>
                        <tr>
                            <th>Issue Id</th>
                            <th>Summary</th>
                        </tr>""" + '\n'

    output_html.write(output)

    tabs += '\t\t'

    match note_type:
        case note_type.RELEASE_NOTE:

            for issue in issues:
                output_html.write("\n" + tabs + "<tr>")
                output_html.write("\t<td>" + issue.jira_id +"</td>\n")
                output_html.write(tabs +"\t<td>" + issue.release_note + "</td>\n")
                output_html.write(tabs +"</tr>")

        case note_type.ENGINEERING_NOTE:

            for issue in issues:

                #Render hyperlinks
                jira = issue_key_to_hyperlink(issue.jira_id)
                output_html.write(tabs + "<tr>\n")
                output_html.write(tabs + "\t<td>" + jira +"</td>\n")
                output_html.write(tabs + "\t<td>" + issue.git_comment + "</td> \n")
                output_html.write(tabs + "</tr>\n")

    closing_tags = """
                    </table>
                </dd>"""

    output_html.write(closing_tags)

def render_epics(output_html, epics, note_type):
    """Render a list of epics"""
    for epic in epics:
        output_html.write("\t\t\t\t<dt>New Feature: " + epic.jira_comment +"</dt> \n")
        output_html.write("\t\t\t\t<dd>\n\t\t\t\t\t" + epic.release_note + "\n\t\t\t\t</dd> \n")

def render_stories(output_html, stories, description, note_type):
    """Render a list of stories to html"""
    render_table_of_issues(output_html, stories, description, note_type)

def render_defects(output_html, defects, description, note_type):
    """Render a list of defects to html"""
    render_table_of_issues(output_html, defects, description, note_type)

def render_support(output_html, support_issues, description, note_type):
    """Render a list of support issues to html"""
    render_table_of_issues(output_html, support_issues, description, note_type)
