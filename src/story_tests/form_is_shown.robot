*** Settings ***
Documentation     User Story: As a user, I see the right form
Library           SeleniumLibrary
Suite Setup       Open Browser    http://127.0.0.1:5001    chrome
Suite Teardown    Close Browser

*** Test Cases ***
User Sees Form After Selecting Reference Type
    [Documentation]    Verify that selecting a reference type displays the correct form
    Go To    http://127.0.0.1:5001
    Select From List By Label    id:form    article
    Click Button    Lisää
    Location Should Contain    http://127.0.0.1:5001/add
    Location Should Contain    form=1
    Page Should Contain    Lisää uusi viite
    Page Should Contain    article
    Page Should Contain    author
    Page Should Contain    publisher
    Go Back

User Sees Right Input Fields For Article
    [Documentation]    Verify that the article form has the correct input fields
    Go To    http://127.0.0.1:5001/add?form=1
    Page Should Contain Element    id:author
    Page Should Contain Element    id:title
    Page Should Contain Element    id:journal
    Page Should Contain Element    id:year
    Page Should Contain Element    id:volume
    Page Should Contain Element    id:number
    Page Should Contain Element    id:pages
    Page Should Contain Element    id:doi
    Page Should Contain Element    id:publisher