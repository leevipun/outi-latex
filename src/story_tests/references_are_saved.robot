*** Settings ***
Documentation     User Story: As a user, I can save a reference
Library           SeleniumLibrary
Suite Setup       Open Browser    http://127.0.0.1:5001    chrome
Suite Teardown    Close Browser

*** Test Cases ***
User Can Save Reference
    [Documentation]    Verify that a user can save a reference and it is stored correctly
    Go To    http://127.0.0.1:5001
    Select From List By Label    id:form    article
    Click Button    + Lisää uusi viite
    Sleep    2s
    Location Should Contain    http://127.0.0.1:5001/add
    Location Should Contain    form=article
    Input Text    id:cite_key    TestArticle2024
    Input Text    id:author    John Doe
    Input Text    id:title    Sample Article Title
    Input Text    id:journal    Journal of Testing
    Input Text    id:year    2024
    Input Text    id:volume    10
    Input Text    id:number    2
    Input Text    id:pages    100-110
    Input Text    id:publisher    Testing Publishers
    Click Button    Tallenna viite
    Sleep    2s
    Location Should Be    http://127.0.0.1:5001/all
    Page Should Contain    John Doe
    Page Should Contain    Sample Article Title
    Page Should Contain    Journal of Testing
    Page Should Contain    2024
