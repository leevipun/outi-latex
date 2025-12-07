*** Settings ***
Documentation     User Story: Users can only see their own references
Library           SeleniumLibrary
Suite Setup       Initialize Test Environment
Suite Teardown    Close Browser

*** Variables ***
${BASE_URL}       http://localhost:5001
${USER1}          robotuser1
${USER2}          robotuser2
${PASS}           robotpass

*** Keywords ***
Initialize Test Environment
    [Documentation]    Initialize the test environment
    Open Browser    ${BASE_URL}    chrome    options=add_argument("--headless");add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage");add_argument("--disable-gpu")
    Set Selenium Speed    0.2s
    Set Selenium Timeout    10s

Create User If Missing
    [Documentation]    Best-effort signup; ignore duplicate user errors
    [Arguments]    ${username}    ${password}
    Go To    ${BASE_URL}/signup
    Input Text    id:username    ${username}
    Input Text    id:password    ${password}
    Click Button    css:button[type="submit"]
    Sleep    0.5s

Login As User
    [Documentation]    Login with credentials
    [Arguments]    ${username}    ${password}
    Go To    ${BASE_URL}/login
    Input Text    id:username    ${username}
    Input Text    id:password    ${password}
    Click Button    css:button[type="submit"]
    Wait Until Page Contains Element    id:form    timeout=5s

Create Test Reference
    [Documentation]    Create a test reference with initial values
    [Arguments]    ${cite_key}    ${author}    ${title}    ${journal}    ${year}    ${volume}    ${number}    ${pages}    ${publisher}
    Go To    ${BASE_URL}
    Select From List By Value    id:form    article
    Click Button    id:add_new-button
    Sleep    2s
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
    Click Button    id:save-reference-button
    Sleep    2s
    Location Should Be    ${BASE_URL}/all

Delete Reference Via UI
    [Documentation]    Delete a reference via UI (must be logged in as owner)
    [Arguments]    ${cite_key}
    Go To    ${BASE_URL}/user
    Sleep    1s
    ${element_exists}=    Run Keyword And Return Status
    ...    Page Should Contain Element    id:reference-key-${cite_key}
    Run Keyword If    ${element_exists}
    ...    Run Keywords
    ...    Click Button    id:delete-button-${cite_key}    AND
    ...    Handle Alert    ACCEPT    AND
    ...    Sleep    1s

Cleanup Test References
    [Documentation]    Clean up any leftover test references (must login first)
    [Arguments]    ${username}    ${password}    @{cite_keys}
    ${is_logged_in}=    Run Keyword And Return Status
    ...    Page Should Contain Element    id:form
    Run Keyword If    not ${is_logged_in}
    ...    Login As User    ${username}    ${password}
    FOR    ${cite_key}    IN    @{cite_keys}
        Delete Reference Via UI    ${cite_key}
    END

*** Test Cases ***
User Can Only See Own References On User Page
    [Documentation]    Verify that user only sees their own references
    [Setup]    Run Keywords
    ...    Create User If Missing    ${USER1}    ${PASS}    AND
    ...    Cleanup Test References    ${USER1}    ${PASS}    User1Ref2024    AND
    ...    Create User If Missing    ${USER2}    ${PASS}    AND
    ...    Cleanup Test References    ${USER2}    ${PASS}    User2Ref2024

    # User1 setup
    Login As User    ${USER1}    ${PASS}
    Create Test Reference    User1Ref2024    John Doe    User 1 Paper    Journal of Testing    2024    10    2    100-110    Testing Publishers

    Go To    ${BASE_URL}/user
    Sleep    1s
    Page Should Contain    User1Ref2024
    Page Should Contain    User 1 Paper

    # Logout
    Go To    ${BASE_URL}/logout
    Wait Until Location Contains    /login    timeout=5s

    # User2 setup
    Login As User    ${USER2}    ${PASS}
    Create Test Reference    User2Ref2024    Jane Smith    User 2 Paper    Journal of Testing    2024    10    2    100-110    Testing Publishers

    Go To    ${BASE_URL}/user
    Sleep    1s
    Page Should Contain    User2Ref2024
    Page Should Not Contain    User1Ref2024

    # Cleanup
    [Teardown]    Run Keywords
    ...    Delete Reference Via UI    User2Ref2024    AND
    ...    Go To    ${BASE_URL}/logout    AND
    ...    Login As User    ${USER1}    ${PASS}    AND
    ...    Delete Reference Via UI    User1Ref2024

User Cannot Edit Other Users References
    [Documentation]    Verify that edit links only appear for own references
    [Setup]    Run Keywords
    ...    Create User If Missing    ${USER1}    ${PASS}    AND
    ...    Cleanup Test References    ${USER1}    ${PASS}    User1Public2024

    # User1 lisää julkisen viitteen
    Login As User    ${USER1}    ${PASS}
    Create Test Reference    User1Public2024    John Doe    User 1 Public    Journal of Testing    2024    10    2    100-110    Testing Publishers

    # Logout
    Go To    ${BASE_URL}/logout
    Wait Until Location Contains    /login    timeout=5s

    # User2 kirjautuu
    Create User If Missing    ${USER2}    ${PASS}
    Login As User    ${USER2}    ${PASS}
    Go To    ${BASE_URL}/all
    Sleep    1s

    # User1:n viite näkyy mutta ei edit-nappia
    Page Should Contain    User1Public2024
    Page Should Not Contain Element    xpath://a[contains(@href, '/edit') and contains(@href, 'User1Public2024')]

    # Cleanup
    [Teardown]    Run Keywords
    ...    Go To    ${BASE_URL}/logout    AND
    ...    Login As User    ${USER1}    ${PASS}    AND
    ...    Delete Reference Via UI    User1Public2024

User Cannot Delete Other Users References
    [Documentation]    Verify that delete button only appears for own references
    [Setup]    Run Keywords
    ...    Create User If Missing    ${USER1}    ${PASS}    AND
    ...    Cleanup Test References    ${USER1}    ${PASS}    User1DeleteTest2024

    # User1 lisää viitteen
    Login As User    ${USER1}    ${PASS}
    Create Test Reference    User1DeleteTest2024    John Doe    User 1 Delete Test    Journal of Testing    2024    10    2    100-110    Testing Publishers

    # Logout
    Go To    ${BASE_URL}/logout
    Wait Until Location Contains    /login    timeout=5s

    # User2 kirjautuu
    Create User If Missing    ${USER2}    ${PASS}
    Login As User    ${USER2}    ${PASS}
    Go To    ${BASE_URL}/all
    Sleep    1s

    # User1:n viite näkyy mutta ei delete-nappia
    Page Should Contain    User1DeleteTest2024
    Page Should Not Contain Element    id:delete-button-User1DeleteTest2024

    # Cleanup
    [Teardown]    Run Keywords
    ...    Go To    ${BASE_URL}/logout    AND
    ...    Login As User    ${USER1}    ${PASS}    AND
    ...    Delete Reference Via UI    User1DeleteTest2024

User Sees All Own References On User Page
    [Documentation]    Verify that user sees all their own references on user page
    [Setup]    Run Keywords
    ...    Create User If Missing    ${USER1}    ${PASS}    AND
    ...    Cleanup Test References    ${USER1}    ${PASS}    FirstRef2024    SecondRef2024

    Login As User    ${USER1}    ${PASS}

    # Lisää kaksi viitettä
    Create Test Reference    FirstRef2024    John Doe    First Paper    Journal of Testing    2024    10    2    100-110    Testing Publishers
    Create Test Reference    SecondRef2024    Jane Smith    Second Paper    Journal of Testing    2024    11    3    200-210    Testing Publishers

    # User-sivulla näkyy molemmat
    Go To    ${BASE_URL}/user
    Sleep    1s
    Page Should Contain    FirstRef2024
    Page Should Contain    SecondRef2024

    # All-sivulla näkyy myös molemmat (julkiset)
    Go To    ${BASE_URL}/all
    Sleep    1s
    Page Should Contain    FirstRef2024
    Page Should Contain    SecondRef2024

    # Cleanup
    [Teardown]    Run Keywords
    ...    Delete Reference Via UI    FirstRef2024    AND
    ...    Delete Reference Via UI    SecondRef2024