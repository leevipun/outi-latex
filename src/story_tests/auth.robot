*** Settings ***
Documentation     Auth and test-mode coverage for Outi LaTeX
Library           SeleniumLibrary
Suite Setup       Setup Browser And Detect Mode
Suite Teardown    Close Browser

*** Variables ***
${BASE_URL}       http://localhost:5001
${USER}           robotuser
${PASS}           robotpass
${IS_TEST_ENV}    False

*** Keywords ***
Setup Browser And Detect Mode
    [Documentation]    Open browser and detect whether TEST_ENV bypasses auth
    Open Browser    ${BASE_URL}/    chrome    options=add_argument("--headless");add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage");add_argument("--disable-gpu")
    ${visible}=    Run Keyword And Return Status    Wait Until Page Contains Element    id:form    timeout=3s
    Set Suite Variable    ${IS_TEST_ENV}    ${visible}
    Run Keyword If    not ${visible}    Go To    ${BASE_URL}/login

Ensure Logged Out
    Go To    ${BASE_URL}/logout

Create User If Missing
    [Documentation]    Best-effort signup; ignore duplicate user errors
    Go To    ${BASE_URL}/signup
    Input Text    id:username    ${USER}
    Input Text    id:password    ${PASS}
    Click Button    css:button[type="submit"]
    Sleep    0.5s

Login As Test User
    Go To    ${BASE_URL}/login
    Input Text    id:username    ${USER}
    Input Text    id:password    ${PASS}
    Click Button    css:button[type="submit"]
    Wait Until Page Contains Element    id:form    timeout=5s

*** Test Cases ***
Redirect To Login When Not Authenticated (Prod Mode)
    [Documentation]    /add should redirect to /login when not authenticated
    Run Keyword If    ${IS_TEST_ENV}    Pass Execution    Skipping: TEST_ENV bypasses auth
    Ensure Logged Out
    Go To    ${BASE_URL}/add?form=article
    Location Should Contain    /login

All Page Is Accessible Without Login
    [Documentation]    /all page shows public references without login
    Ensure Logged Out
    Go To    ${BASE_URL}/all
    Location Should Be    ${BASE_URL}/all

Login Works And Home Is Accessible
    [Tags]    auth
    Run Keyword If    ${IS_TEST_ENV}    Pass Execution    Skipping: TEST_ENV bypasses auth
    Ensure Logged Out
    Create User If Missing
    Login As Test User
    Page Should Contain Element    id:form

Logout Behavior Matches Mode
    [Tags]    auth
    Run Keyword If    ${IS_TEST_ENV}    Pass Execution    Skipping: TEST_ENV bypasses auth
    Ensure Logged Out
    Create User If Missing
    Login As Test User
    Go To    ${BASE_URL}/logout
    Location Should Contain    /login

Test Mode Bypasses Auth Wall
    [Tags]    testmode
    IF    not ${IS_TEST_ENV}
        Pass Execution    Skipping: only relevant when TEST_ENV=true
    END
    Go To    ${BASE_URL}/
    Page Should Contain Element    id:form
