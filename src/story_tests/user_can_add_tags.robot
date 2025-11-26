*** Settings ***
Documentation     User Story: User can add TAG reference
Library           SeleniumLibrary
Library           RequestsLibrary
Suite Setup       Initialize Test Environment
Suite Teardown    Close Browser

*** Variables ***
${BASE_URL}       http://localhost:5001

*** Keywords ***
Initialize Test Environment
    [Documentation]    Initialize the test environment
    Open Browser    ${BASE_URL}    chrome    options=add_argument("--headless");add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage");add_argument("--disable-gpu")

Create Test Reference
    [Documentation]    Create a test reference with initial values
    [Arguments]    ${cite_key}    ${author}    ${title}    ${journal}    ${year}    ${volume}    ${number}    ${pages}    ${publisher}    ${tag}
    Go To    ${BASE_URL}
    Select From List By Value    id:form    article
    Click Button    id:add_new-button
    Sleep    1s
    Location Should Contain    ${BASE_URL}/add?form=article
    Input Text    id:cite_key    ${cite_key}
    Input Text    id:author    ${author}
    Input Text    id:title    ${title}
    Input Text    id:journal    ${journal}
    Input Text    id:year    ${year}
    Input Text    id:volume    ${volume}
    Input Text    id:number    ${number}
    Input Text    id:pages    ${pages}
    Input Text    id:publisher    ${publisher}
    Input Text    id:new_tag    ${tag}
    Click Button    id:save-reference-button
    Wait Until Page Contains Element    id:all-references-title    timeout=5s

Delete Test Reference
    [Documentation]    Delete a test reference by its cite key
    [Arguments]    ${cite_key}
    Go To    ${BASE_URL}/all
    Page Should Contain Element    id:reference-key-${cite_key}
    Click Button    id:delete-button-${cite_key}
    Handle Alert    ACCEPT
    Wait Until Page Contains Element    id:all-references-title    timeout=5s
    Page Should Not Contain Element    id:reference-key-${cite_key}

*** Test Cases ***
User Can Create Tag
    [Documentation]    Verify that a tag created in creating a reference is shown
    [Setup]    Create Test Reference    TagArticle    Test Author    Test Title    Test Journal    2001    8    1    1-3    Test Publisher    test tag
    [Teardown]    Delete Test Reference    TagArticle

    Go To    ${BASE_URL}/all
    Sleep    2s
    Page Should Contain Element    id:reference-key-TagArticle
    Element Text Should Be    id:value-TagArticle-tag    test tag
