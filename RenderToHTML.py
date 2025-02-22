# Render the content of various lists to a predefined HTML format
# <Header>
# <List of Epics>
# <List of Stories>
# <list of Defects>
# <list of Support issues>

def RenderToHTML(outputLocation, version, previousVersion, renderIgnoredIssues, epicList, storyList, defectList, supportList, otherList):

    with open(outputLocation, "w") as outputHTML:        

        RenderHeader(outputHTML)

        RenderBody(outputHTML, version, previousVersion)
        RenderEpics(outputHTML, epicList, "Yes")
        RenderStories(outputHTML, storyList, "Yes", "Minor enhancements made to device software")
        RenderDefects(outputHTML, defectList, "Yes", "Defects resolved in device software")
        RenderSupport(outputHTML, supportList, "Yes", "Customer support issues resolved in device software")

        #Render issues that are not suitable for release notes
        RenderHorizontalLine(outputHTML)

        if(renderIgnoredIssues):
            RenderIgnoredEpics(outputHTML, epicList, "No")
            RenderStories(outputHTML, storyList, "No", "Stories to ignore from release notes")
            RenderDefects(outputHTML, defectList, "No", "Defects to ignore from release notes")
            RenderSupport(outputHTML, supportList, "No", "Support issues to ignore from release notes")

        RenderCloseBody(outputHTML)

    outputHTML.close()        

def RenderHorizontalLine(outputHTML):
    outputHTML.write("<hr>")

def RenderHeader(outputHTML):

    # Write the HTML Header

    #TODO: Set the release notes title correctly        
    htmlcode = """<html lang="en">
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
       
    outputHTML.write(htmlcode)

def RenderBody(outputHTML, version, previousVersion):

    # Write the HTML Body text

    htmlBody = """
    <body>
        <div class="releaseNotes">
            <h1>Motorola Solutions device release notes - """
    
    htmlBodyNext = "</h1>" + """
            <!--<p><em>Warning:</em> These release notes are incomplete, expect an update</p>-->
            <h2>Changes</h2>
            <hr>"""

    htmlSoftwareVersion = "<h3>Software updated in " + version + "</h3>"

    htmlBodyTail = """
            <ul>
                <li>V500 firmware
                <li>VB400 firmware
                <!--<li>VT50 / VT100 firmware-->
                <li>DockController firmware
                <li>Smart Dock firmware
            </ul>"""
    
    since = "<h3>Changes since " + previousVersion + "</h3>" + """
            <dl>\n"""

    htmlContent = htmlBody + htmlBodyNext + htmlSoftwareVersion + htmlBodyTail + since    
    outputHTML.write(htmlContent)

def RenderCloseBody(outputHTML):

    # Write the HTML body closing tags

    closeBody = "</body>"

    then = """   
            <dl>
        </div>\n"""    
    
    outputHTML.write(then + closeBody)

def RenderTableOfIssues(outputHTML, issues, header, takeReleaseNote):    

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

    for issue in issues:
        if(issue.Take == takeReleaseNote):
            outputHTML.write("\t\t\t\t<tr>")
            outputHTML.write("\t\t\t\t\t<td>" + issue.JiraId +"</td>\n")

            if(takeReleaseNote == "Yes"):
                outputHTML.write("\t\t\t\t\t<td>" + issue.ActualReleaseNote + "\n\t\t\t\t</td> \n")
            else:
                outputHTML.write("\t\t\t\t\t<td>" + issue.ActualReleaseNote + "\n\t\t\t\t</td> \n")
            outputHTML.write("\t\t\t\t</tr>")
    
    closingTags = """
                    </table>
                </dd>"""

    outputHTML.write(closingTags)

def RenderEpics(outputHTML, EpicsList, takeReleaseNote):
    for epic in EpicsList:

        if(epic.Take == takeReleaseNote):
            outputHTML.write("\t\t\t\t<dt>New Feature: " + epic.JiraComment +"</dt> \n")
            outputHTML.write("\t\t\t\t<dd>\n\t\t\t\t\t" + epic.ActualReleaseNote + "\n\t\t\t\t</dd> \n")

def RenderIgnoredEpics(outputHTML, epics, takeReleaseNote):
    RenderTableOfIssues(outputHTML, epics, "Epics to ignore for release notes", takeReleaseNote)

def RenderStories(outputHTML, stories, takeReleaseNote, description):
    RenderTableOfIssues(outputHTML, stories, description, takeReleaseNote)

def RenderDefects(outputHTML, defects, takeReleaseNote, description):
    RenderTableOfIssues(outputHTML, defects, description, takeReleaseNote)


def RenderSupport(outputHTML, supportIssues, takeReleaseNote, description):
    RenderTableOfIssues(outputHTML, supportIssues, description, takeReleaseNote)      
