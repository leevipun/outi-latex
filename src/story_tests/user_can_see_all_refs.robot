*** Settings ***
Documentation     User Story: As a user, I can choose reference type (book, article...)
Library           SeleniumLibrary
Suite Setup       Open Browser    http://127.0.0.1:5001    chrome
Suite Teardown    Close Browser


*** Test Cases ***        
User Can See All Added Reference Types
    [Documentation]    Verify that the all references page displays all added references
    Go To    http://127.0.0.1:5001/all
    Page Should Contain    Tässä kaikki lisäämäsi viitteet
    Element Should Be Visible    id:refs_table

User Can See Added Article Reference
    [Documentation]    Verify that an added article reference is displayed correctly
    Go To    http://127.0.0.1:5001/all
    Page Should Contain    zimmerman2002becoming
    Page Should Contain    article
