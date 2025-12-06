*** Settings ***
Documentation     User Story: As a user, I can make the reference public or private
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

Delete Test Reference
    [Documentation]    Delete a test reference by its cite key
    [Arguments]    ${cite_key}
    Go To    ${BASE_URL}/all
    ${exists}=    Run Keyword And Return Status    Page Should Contain Element    id:reference-item-${cite_key}
    Run Keyword If    ${exists}    Run Keywords
    ...    Wait Until Element Is Visible    xpath://div[@id='reference-item-${cite_key}']//button[contains(text(), 'Poista')]    timeout=5s
    ...    AND    Click Element    xpath://div[@id='reference-item-${cite_key}']//button[contains(text(), 'Poista')]
    ...    AND    Handle Alert    ACCEPT
    ...    AND    Wait Until Page Does Not Contain Element    id:reference-item-${cite_key}    timeout=5s

Delete Private Test Reference
    [Documentation]    Delete a private test reference via edit page
    [Arguments]    ${cite_key}
    Go To    ${BASE_URL}/edit/${cite_key}
    ${exists}=    Run Keyword And Return Status    Page Should Contain Element    xpath://button[contains(text(), 'Poista')]
    Run Keyword If    ${exists}    Run Keywords
    ...    Wait Until Element Is Visible    xpath://button[contains(text(), 'Poista')]    timeout=5s
    ...    AND    Click Element    xpath://button[contains(text(), 'Poista')]
    ...    AND    Handle Alert    ACCEPT

*** Test Cases ***
User Can Add Public Reference
    [Documentation]    Test that user can add a public reference (default)
    [Teardown]    Delete Test Reference    TestPublic2024

    Go To    ${BASE_URL}
    Wait Until Element Is Visible    id:form    timeout=10s
    Wait Until Element Is Enabled    id:form    timeout=5s
    Select From List By Value    id:form    article
    Wait Until Element Is Visible    id:add_new-button    timeout=5s
    Wait Until Element Is Enabled    id:add_new-button    timeout=5s
    Click Button    id:add_new-button
    Wait Until Location Contains    /add?form=article    timeout=10s
    Wait Until Element Is Visible   id:cite_key    timeout=5s
    Input Text    id:cite_key    TestPublic2024
    Input Text    id:author    Test Author
    Input Text    id:title    Test Title
    Input Text    id:journal    Test Journal
    Input Text    id:year    2024
    Wait Until Page Contains Element    id:visibility-toggle    timeout=5s
    Checkbox Should Be Selected    id:visibility-toggle
    Wait Until Element Is Visible    id:save-reference-button    timeout=5s
    Click Button    id:save-reference-button
    Wait Until Location Contains    /all    timeout=15s
    Wait Until Page Contains Element    id:reference-item-TestPublic2024    timeout=5s
    Page Should Contain    TestPublic2024
    Page Should Contain    Test Author

User Can Add Private Reference
    [Documentation]    Test that user can add a private reference
    [Teardown]    Delete Private Test Reference    TestPrivate2024

    Go To    ${BASE_URL}
    Wait Until Element Is Visible    id:form    timeout=10s
    Wait Until Element Is Enabled    id:form    timeout=5s
    Select From List By Value    id:form    article
    Wait Until Element Is Visible    id:add_new-button    timeout=5s
    Wait Until Element Is Enabled    id:add_new-button    timeout=5s
    Click Button    id:add_new-button
    Wait Until Location Contains    /add?form=article    timeout=10s
    Wait Until Element Is Visible   id:cite_key    timeout=5s
    Input Text    id:cite_key    TestPrivate2024
    Input Text    id:author    Private Author
    Input Text    id:title    Private Title
    Input Text    id:journal    Test Journal
    Input Text    id:year    2024
    Wait Until Page Contains Element    id:visibility-toggle    timeout=5s
    Execute Javascript    document.getElementById('visibility-toggle').checked = false;
    Wait Until Element Is Visible    id:save-reference-button    timeout=5s
    Click Button    id:save-reference-button
    Wait Until Location Contains    /all    timeout=15s
    Page Should Not Contain    TestPrivate2024
    Page Should Not Contain    Private Author
