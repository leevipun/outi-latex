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
    Create Session    api    ${BASE_URL}

Delete Reference Via API
    [Documentation]    Delete a reference via API (works for both public and private)
    [Arguments]    ${cite_key}
    ${response}=    Run Keyword And Ignore Error
    ...    DELETE On Session    api    /delete/${cite_key}    expected_status=any
    Log    Attempted to delete ${cite_key}

Toggle Visibility Switch
    [Documentation]    Click the toggle switch to change visibility
    Wait Until Page Contains Element    css:.toggle-switch    timeout=5s
    Click Element    css:.toggle-switch
    Sleep    0.2s

*** Test Cases ***
User Can Add Public Reference
    [Documentation]    Test that user can add a public reference (default)
    [Setup]    Delete Reference Via API    TestPublic2024
    [Teardown]    Delete Reference Via API    TestPublic2024

    Go To    ${BASE_URL}
    Wait Until Element Is Visible    id:form    timeout=10s
    Select From List By Value    id:form    article
    Wait Until Element Is Visible    id:add_new-button    timeout=5s
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
    Click Button    id:save-reference-button
    Wait Until Location Contains    /all    timeout=30s
    Wait Until Page Contains Element    id:reference-item-TestPublic2024    timeout=5s
    Page Should Contain    TestPublic2024

User Can Add Private Reference
    [Documentation]    Test that user can add a private reference
    [Setup]    Delete Reference Via API    TestPrivate2024
    [Teardown]    Delete Reference Via API    TestPrivate2024

    Go To    ${BASE_URL}
    Wait Until Element Is Visible    id:form    timeout=10s
    Select From List By Value    id:form    article
    Wait Until Element Is Visible    id:add_new-button    timeout=5s
    Click Button    id:add_new-button
    Wait Until Location Contains    /add?form=article    timeout=10s
    Wait Until Element Is Visible   id:cite_key    timeout=5s
    Input Text    id:cite_key    TestPrivate2024
    Input Text    id:author    Private Author
    Input Text    id:title    Private Title
    Input Text    id:journal    Test Journal
    Input Text    id:year    2024
    Toggle Visibility Switch
    Element Attribute Value Should Be    id:visibility-value    value    private
    Click Button    id:save-reference-button
    Wait Until Location Contains    /all    timeout=60s
    Page Should Not Contain    TestPrivate2024

Private Reference Not Shown On All Page
    [Documentation]    Verify that private reference is not visible on /all page
    [Setup]    Delete Reference Via API    PrivateTest2024
    [Teardown]    Delete Reference Via API    PrivateTest2024

    Go To    ${BASE_URL}
    Wait Until Element Is Visible    id:form    timeout=10s
    Select From List By Value    id:form    article
    Wait Until Element Is Visible    id:add_new-button    timeout=5s
    Click Button    id:add_new-button
    Wait Until Location Contains    /add?form=article    timeout=10s
    Wait Until Element Is Visible    id:cite_key    timeout=5s
    Input Text    id:cite_key    PrivateTest2024
    Input Text    id:author    Private Author
    Input Text    id:title    Private Title
    Input Text    id:journal    Test Journal
    Input Text    id:year    2024
    Toggle Visibility Switch
    Element Attribute Value Should Be    id:visibility-value    value    private
    Click Button    id:save-reference-button
    Wait Until Location Contains    /all    timeout=30s

    Go To    ${BASE_URL}/all
    Page Should Not Contain Element    id:reference-item-PrivateTest2024
    Page Should Not Contain    PrivateTest2024

Public Reference Is Shown On All Page
    [Documentation]    Verify that public reference is visible on /all page
    [Setup]    Delete Reference Via API    PublicTest2024
    [Teardown]    Delete Reference Via API    PublicTest2024

    Go To    ${BASE_URL}
    Wait Until Element Is Visible    id:form    timeout=10s
    Select From List By Value    id:form    article
    Wait Until Element Is Visible    id:add_new-button    timeout=5s
    Click Button    id:add_new-button
    Wait Until Location Contains    /add?form=article    timeout=10s
    Wait Until Element Is Visible    id:cite_key    timeout=5s
    Input Text    id:cite_key    PublicTest2024
    Input Text    id:author    Public Author
    Input Text    id:title    Public Title
    Input Text    id:journal    Test Journal
    Input Text    id:year    2024
    Click Button    id:save-reference-button
    Wait Until Location Contains    /all    timeout=30s

    Go To    ${BASE_URL}/all
    Wait Until Page Contains Element    id:reference-item-PublicTest2024    timeout=5s
    Page Should Contain    PublicTest2024

User Can Change Visibility From Public To Private
    [Documentation]    Test changing reference from public to private
    [Setup]    Delete Reference Via API    VisibilityTest2024
    [Teardown]    Delete Reference Via API    VisibilityTest2024

    Go To    ${BASE_URL}
    Wait Until Element Is Visible    id:form    timeout=10s
    Select From List By Value    id:form    article
    Wait Until Element Is Visible    id:add_new-button    timeout=5s
    Click Button    id:add_new-button
    Wait Until Location Contains    /add?form=article    timeout=10s
    Wait Until Element Is Visible    id:cite_key    timeout=5s
    Input Text    id:cite_key    VisibilityTest2024
    Input Text    id:author    Test Author
    Input Text    id:title    Test Title
    Input Text    id:journal    Test Journal
    Input Text    id:year    2024
    Click Button    id:save-reference-button
    Wait Until Location Contains    /all    timeout=30s

    Wait Until Page Contains Element    id:reference-item-VisibilityTest2024    timeout=10s
    Go To    ${BASE_URL}/edit/VisibilityTest2024

    Wait Until Location Contains    /edit/VisibilityTest2024    timeout=10s
    Wait Until Page Contains Element    id:visibility-toggle    timeout=5s
    Checkbox Should Be Selected    id:visibility-toggle
    Toggle Visibility Switch
    Element Attribute Value Should Be    id:visibility-value    value    private
    Click Button    id:save-reference-button
    Wait Until Location Contains    /all    timeout=30s

    Page Should Not Contain Element    id:reference-item-VisibilityTest2024

User Can Change Visibility From Private To Public
    [Documentation]    Test changing reference from private to public
    [Setup]    Delete Reference Via API    PrivToPublic2024
    [Teardown]    Delete Reference Via API    PrivToPublic2024

    Go To    ${BASE_URL}
    Wait Until Element Is Visible    id:form    timeout=10s
    Select From List By Value    id:form    article
    Wait Until Element Is Visible    id:add_new-button    timeout=5s
    Click Button    id:add_new-button
    Wait Until Location Contains    /add?form=article    timeout=10s
    Wait Until Element Is Visible    id:cite_key    timeout=5s
    Input Text    id:cite_key    PrivToPublic2024
    Input Text    id:author    Test Author
    Input Text    id:title    Test Title
    Input Text    id:journal    Test Journal
    Input Text    id:year    2024
    Toggle Visibility Switch
    Element Attribute Value Should Be    id:visibility-value    value    private
    Click Button    id:save-reference-button
    Wait Until Location Contains    /all    timeout=30s

    Page Should Not Contain Element    id:reference-item-PrivToPublic2024

    Go To    ${BASE_URL}/edit/PrivToPublic2024
    Wait Until Page Contains Element    id:visibility-toggle    timeout=5s
    Checkbox Should Not Be Selected    id:visibility-toggle
    Toggle Visibility Switch
    Element Attribute Value Should Be    id:visibility-value    value    public
    Click Button    id:save-reference-button
    Wait Until Location Contains    /all    timeout=30s

    Wait Until Page Contains Element    id:reference-item-PrivToPublic2024    timeout=5s

Default Visibility Is Public
    [Documentation]    New references should be public by default
    Go To    ${BASE_URL}
    Wait Until Element Is Visible    id:form    timeout=10s
    Select From List By Value    id:form    article
    Wait Until Element Is Visible    id:add_new-button    timeout=5s
    Click Button    id:add_new-button
    Wait Until Location Contains    /add?form=article    timeout=10s
    Wait Until Page Contains Element    id:visibility-toggle    timeout=5s
    Checkbox Should Be Selected    id:visibility-toggle
    Wait Until Page Contains Element    id:visibility-value    timeout=5s
    Element Attribute Value Should Be    id:visibility-value    value    public

Visibility Toggle Is Present
    [Documentation]    Visibility toggle should be visible on forms
    Go To    ${BASE_URL}
    Wait Until Element Is Visible    id:form    timeout=10s
    Select From List By Value    id:form    article
    Wait Until Element Is Visible    id:add_new-button    timeout=5s
    Click Button    id:add_new-button
    Wait Until Location Contains    /add?form=article    timeout=10s
    Wait Until Page Contains Element    id:visibility-toggle    timeout=5s
    Page Should Contain Element    id:visibility-toggle
    Page Should Contain Element    id:visibility-value
    Page Should Contain    📢 Julkinen
