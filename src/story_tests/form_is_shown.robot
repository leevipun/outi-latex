*** Settings ***
Documentation     User Story: As a user, I see the right form
Library           SeleniumLibrary
Library           RequestsLibrary
Suite Setup       Initialize Test Environment
Suite Teardown    Close Browser

*** Variables ***
${BASE_URL}       http://localhost:5001
${USER}           robotuser
${PASS}           robotpass

*** Keywords ***
Initialize Test Environment
    [Documentation]    Initialize the test environment
    Open Browser    ${BASE_URL}    chrome    options=add_argument("--headless");add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage");add_argument("--disable-gpu")

    Run Keyword And Ignore Error    Create User If Missing
    Login As Test User

Create User If Missing
    [Documentation]    Best-effort signup; ignore duplicate user errors
    Go To    ${BASE_URL}/signup
    Input Text    id:username    ${USER}
    Input Text    id:password    ${PASS}
    Click Button    css:button[type="submit"]
    Sleep    0.5s

Login As Test User
    [Documentation]    Login with test credentials
    Go To    ${BASE_URL}/login
    Input Text    id:username    ${USER}
    Input Text    id:password    ${PASS}
    Click Button    css:button[type="submit"]
    Wait Until Page Contains Element    id:form    timeout=5s

*** Test Cases ***
User Sees Form After Selecting Reference Type
    [Documentation]    Verify that selecting a reference type displays the correct form
    Go To    ${BASE_URL}
    Select From List By Value    id:form    article
    Click Button    id:add_new-button
    Wait Until Page Contains Element    id:add-reference-form    timeout=5s
    Location Should Contain    ${BASE_URL}/add
    Page Should Contain Element    id:add-reference-form
    Page Should Contain Element    id:reference-type-heading
    Page Should Contain Element    id:author
    Page Should Contain Element    id:cite_key
    Click Link    id:back-to-home

User Sees Right Input Fields For Article
    [Documentation]    Verify that the article form has the correct input fields
    Go To    ${BASE_URL}/add?form=article
    Page Should Contain Element    id:cite_key
    Page Should Contain Element    id:author
    Page Should Contain Element    id:title
    Page Should Contain Element    id:journal
    Page Should Contain Element    id:year
    Page Should Contain Element    id:volume
    Page Should Contain Element    id:number
    Page Should Contain Element    id:pages
    Page Should Contain Element    id:doi
    Page Should Contain Element    id:publisher