# Render the content of various lists to a predefined HTML format
# <Header>
# <List of Epics>
# <List of Stories>
# <list of Defects>
# <list of Support issues>

from NoteType import ReleaseNoteType

def RenderToHTML(outputLocation, version, previousVersion, renderIgnoredIssues, epicList, storyList, defectList, supportList, otherList, noteType):

    with open(outputLocation, "w") as outputHTML:        

        RenderHeader(outputHTML)

        RenderBody(outputHTML, version, previousVersion, noteType)
        RenderEpics(outputHTML, epicList, noteType)
        RenderStories(outputHTML, storyList, "Minor enhancements made to device software", noteType)
        RenderDefects(outputHTML, defectList, "Defects resolved in device software", noteType)
        RenderSupport(outputHTML, supportList, "Customer support issues resolved in device software", noteType)

        #Render issues that are not suitable for release notes
        RenderHorizontalLine(outputHTML)

        if(renderIgnoredIssues):
            RenderIgnoredEpics(outputHTML, epicList)
            RenderStories(outputHTML, storyList, "Stories to ignore from release notes")
            RenderDefects(outputHTML, defectList, "Defects to ignore from release notes")
            RenderSupport(outputHTML, supportList, "Support issues to ignore from release notes")

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

def RenderBody(outputHTML, version, previousVersion, noteType):

    # Write the HTML Body text

    htmlBody = """
    <body>
        <div class="releaseNotes">
            <h1>Motorola Solutions release notes - """
    
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

    if(noteType == noteType.RELEASE_NOTE):
        htmlContent = htmlBody + htmlBodyNext + htmlSoftwareVersion + htmlBodyTail + since    
    else:
        htmlContent = htmlBody + htmlBodyNext + htmlSoftwareVersion + since

    outputHTML.write(htmlContent)

def RenderCloseBody(outputHTML):

    # Write the HTML body closing tags

    closeBody = "</body>"

    then = """   
            <dl>
        </div>\n"""    
    
    outputHTML.write(then + closeBody)

def RenderTableOfIssues(outputHTML, issues, header, noteType):   

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
                    outputHTML.write("\t\t\t\t\t<td>" + issue.jiraId +"</td>\n")
                    outputHTML.write("\t\t\t\t\t<td>" + issue.release_note + "\n\t\t\t\t</td> \n")
                    outputHTML.write("\t\t\t\t</tr>")

        case noteType.ENGINEERING_NOTE:

            for issue in issues:
                    
                    #Render hyperlinks
                    jiraID = issue.jiraId
                    dashLocation = -1
                    url = ""

                    # AZMV issues are in AZDO
                    if(jiraID.startswith(("AZMV", "azmv"))):
                       
                       dashLocation = jiraID.find('-')
                       length = len(jiraID)

                       if(dashLocation != -1):
                            azdoId = jiraID[dashLocation+1:length]
                            url = 'https://dev.azure.com/MobileVideo/VideoManager/_workitems/edit/' + azdoId
                            
                    else:                    
                        # Assume the issue is a Jira instead                        
                        url = "https://jira.mot-solutions.com/browse/" + jiraID

                    jiraID = '<a href="' + url + '">' + issue.jiraId + '</a>'

                    outputHTML.write("\t\t\t\t<tr>")
                    outputHTML.write("\t\t\t\t\t<td>" + jiraID +"</td>\n")
                    outputHTML.write("\t\t\t\t\t<td>" + issue.gitComment + "\n\t\t\t\t</td> \n")
                    outputHTML.write("\t\t\t\t</tr>")
    
    closingTags = """
                    </table>
                </dd>"""

    outputHTML.write(closingTags)

def RenderEpics(outputHTML, EpicsList, noteType):
    for epic in EpicsList:
            outputHTML.write("\t\t\t\t<dt>New Feature: " + epic.jiraComment +"</dt> \n")
            outputHTML.write("\t\t\t\t<dd>\n\t\t\t\t\t" + epic.release_note + "\n\t\t\t\t</dd> \n")

def RenderIgnoredEpics(outputHTML, epics, noteType):
    RenderTableOfIssues(outputHTML, epics, "Epics to ignore for release notes")

def RenderStories(outputHTML, stories, description, noteType):
    RenderTableOfIssues(outputHTML, stories, description, noteType)

def RenderDefects(outputHTML, defects, description, noteType):
    RenderTableOfIssues(outputHTML, defects, description, noteType)


def RenderSupport(outputHTML, supportIssues, description, noteType):
    RenderTableOfIssues(outputHTML, supportIssues, description, noteType)      
