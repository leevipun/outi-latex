*** Settings ***
Documentation     User Story: User can switch to dark mode
Library           SeleniumLibrary
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
    Create User If Missing
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
User Can Switch From Light Mode To Dark Mode
    [Documentation]    Verify that user can switch from light mode to dark mode
    Go To    ${BASE_URL}
    Page Should Contain Element    id:theme-toggle
    ${aria_label}=    Get Element Attribute    id:theme-toggle    aria-label
    Should Contain    ${aria_label}    tummaan
    Click Link    id:theme-toggle
    Wait Until Page Contains Element    id:theme-toggle    timeout=5s
    ${aria_label}=    Get Element Attribute    id:theme-toggle    aria-label
    Should Contain    ${aria_label}    vaaleaan

User Can Switch Back To Light Mode
    [Documentation]    Verify that user can switch back from dark mode to light mode
    Go To    ${BASE_URL}
    Delete All Cookies
    Go To    ${BASE_URL}
    ${aria_label}=    Get Element Attribute    id:theme-toggle    aria-label
    Should Contain    ${aria_label}    tummaan
    Click Link    id:theme-toggle
    Wait Until Page Contains Element    id:theme-toggle    timeout=5s
    ${aria_label}=    Get Element Attribute    id:theme-toggle    aria-label
    Should Contain    ${aria_label}    vaaleaan
    Click Link    id:theme-toggle
    Wait Until Page Contains Element    id:theme-toggle    timeout=5s
    ${aria_label}=    Get Element Attribute    id:theme-toggle    aria-label
    Should Contain    ${aria_label}    tummaan

Dark Mode Preference Is Persisted
    [Documentation]    Verify that dark mode preference is saved and persisted on page reload
    Go To    ${BASE_URL}
    Delete All Cookies
    Go To    ${BASE_URL}
    Click Link    id:theme-toggle
    Wait Until Page Contains Element    id:theme-toggle    timeout=5s
    ${aria_label_before}=    Get Element Attribute    id:theme-toggle    aria-label
    Reload Page
    Wait Until Page Contains Element    id:theme-toggle    timeout=5s
    ${aria_label_after}=    Get Element Attribute    id:theme-toggle    aria-label
    Should Be Equal    ${aria_label_before}    ${aria_label_after}
