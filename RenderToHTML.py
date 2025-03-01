# Render the content of various lists to a predefined HTML format
# <Header>
# <List of Epics>
# <List of Stories>
# <list of Defects>
# <list of Support issues>

def render_to_html(output_location, version, previous_version, render_ignored_issues, epics, stories, defects, support_issues, other, note_type):

    with open(output_location, "w") as output_html:        

        render_header(output_html)

        render_body(output_html, version, previous_version, note_type)
        render_epics(output_html, epics, note_type)
        render_stories(output_html, stories, "Minor enhancements made to device software", note_type)
        render_defects(output_html, defects, "Defects resolved in device software", note_type)
        render_support(output_html, support_issues, "Customer support issues resolved in device software", note_type)

        #Render issues that are not suitable for release notes
        render_horizontal_line(output_html)

        if(render_ignored_issues):
            render_ignored_epics(output_html, epics, note_type)
            render_stories(output_html, stories, "Stories to ignore from release notes", note_type)
            render_defects(output_html, defects, "Defects to ignore from release notes", note_type)
            render_support(output_html, support_issues, "Support issues to ignore from release notes", note_type)

        render_close_body(output_html)

    output_html.close()

def render_horizontal_line(output):
    output.write("<hr>")

def render_header(output):

    # Write the HTML Header

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
       
    output.write(html)

def render_body(html, version, previous_version, note_type):

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

    if(note_type == note_type.RELEASE_NOTE):
        content = html_body + next + software_version + tail + since    
    else:
        content = html_body + next + software_version + since

    html.write(content)

def render_close_body(outputHTML):

    # Write the HTML body closing tags

    closeBody = "</body>"

    then = """   
            <dl>
        </div>\n"""    
    
    outputHTML.write(then + closeBody)

def render_table_of_issues(outputHTML, issues, header, noteType):   

    # Render a table of issues
    outputHTML.write("<dt>" + header + "</dt>")
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
                        </tr>"""    
    
    outputHTML.write(output)

    match noteType:
        case noteType.RELEASE_NOTE:

            for issue in issues:
                    outputHTML.write("\t\t\t\t<tr>")
                    outputHTML.write("\t\t\t\t\t<td>" + issue.jira_id +"</td>\n")
                    outputHTML.write("\t\t\t\t\t<td>" + issue.release_note + "\n\t\t\t\t</td> \n")
                    outputHTML.write("\t\t\t\t</tr>")

        case noteType.ENGINEERING_NOTE:

            for issue in issues:
                    
                    #Render hyperlinks
                    jira_id = issue.jira_id
                    dash_location = -1
                    url = ""

                    # AZMV issues are in AZDO
                    if(jira_id.startswith(("AZMV", "azmv"))):
                       
                       dash_location = jira_id.find('-')
                       length = len(jira_id)

                       if(dash_location != -1):
                            azdo_id = jira_id[dash_location+1:length]
                            url = 'https://dev.azure.com/MobileVideo/VideoManager/_workitems/edit/' + azdo_id
                            
                    else:                    
                        # Assume the issue is a Jira instead                        
                        url = "https://jira.mot-solutions.com/browse/" + jira_id

                    jira_id = '<a href="' + url + '">' + issue.jira_id + '</a>'

                    outputHTML.write("\t\t\t\t<tr>")
                    outputHTML.write("\t\t\t\t\t<td>" + jira_id +"</td>\n")
                    outputHTML.write("\t\t\t\t\t<td>" + issue.git_comment + "\n\t\t\t\t</td> \n")
                    outputHTML.write("\t\t\t\t</tr>")
    
    closingTags = """
                    </table>
                </dd>"""

    outputHTML.write(closingTags)

def render_epics(outputHTML, EpicsList, noteType):
    for epic in EpicsList:
            outputHTML.write("\t\t\t\t<dt>New Feature: " + epic.jira_comment +"</dt> \n")
            outputHTML.write("\t\t\t\t<dd>\n\t\t\t\t\t" + epic.release_note + "\n\t\t\t\t</dd> \n")

def render_ignored_epics(outputHTML, epics, noteType):
    render_table_of_issues(outputHTML, epics, "Epics to ignore for release notes")

def render_stories(outputHTML, stories, description, noteType):
    render_table_of_issues(outputHTML, stories, description, noteType)

def render_defects(outputHTML, defects, description, noteType):
    render_table_of_issues(outputHTML, defects, description, noteType)


def render_support(outputHTML, supportIssues, description, noteType):
    render_table_of_issues(outputHTML, supportIssues, description, noteType)      
