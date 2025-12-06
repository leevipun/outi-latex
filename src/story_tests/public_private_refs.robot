*** Settings ***
Documentation     User Story: As a user, I can make the reference public or private
Library           SeleniumLibrary
Library           RequestsLibrary
Suite Setup       Initialize Test Environment And Create Test Data
Suite Teardown    Clean Up Test Data And Close Browser

*** Variables ***
${BASE_URL}       http://localhost:5001

*** Keywords ***
Initialize Test Environment And Create Test Data
    [Documentation]    Initialize the test environment and create test data once for all tests
    Open Browser    ${BASE_URL}    chrome    options=add_argument("--headless");add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage");add_argument("--disable-gpu")
    Create Test References For Public Private

Clean Up Test Data And Close Browser
    [Documentation]    Clean up test data and close browser after all tests
    Delete Test References For Public Private
    Close Browser

Create Test References For Public Private
    [Documentation]    Create test references with different visibility settings
    Go To    ${BASE_URL}

    # Create first public reference
    Select From List By Value    id:form    article
    Click Button    id:add_new-button
    Wait Until Location Contains    /add?form=article    timeout=10s
    Wait Until Element Is Visible   id:cite_key    timeout=5s
    Input Text    id:cite_key    PublicRef2024
    Input Text    id:author      Public Author
    Input Text    id:title       Public Paper Title
    Input Text    id:journal     Public Journal
    Input Text    id:year        2024
    # Visibility toggle should be checked by default
    Checkbox Should Be Selected    id:visibility-toggle
    Click Button    id:save-reference-button
    Wait Until Location Contains    /all    timeout=15s
    Sleep    1s

    # Create private reference
    Go To    ${BASE_URL}
    Sleep    1s
    Select From List By Value    id:form    article
    Click Button    id:add_new-button
    Wait Until Location Contains    /add?form=article    timeout=10s
    Wait Until Element Is Visible   id:cite_key    timeout=5s
    Input Text    id:cite_key    PrivateRef2024
    Input Text    id:author      Private Author
    Input Text    id:title       Private Paper Title
    Input Text    id:journal     Private Journal
    Input Text    id:year        2024
    # Uncheck visibility toggle to make it private
    Unselect Checkbox    id:visibility-toggle
    Click Button    id:save-reference-button
    Wait Until Location Contains    /all    timeout=15s
    Sleep    1s

    # Create another public reference
    Go To    ${BASE_URL}
    Sleep    1s
    Select From List By Value    id:form    article
    Click Button    id:add_new-button
    Wait Until Location Contains    /add?form=article    timeout=10s
    Wait Until Element Is Visible   id:cite_key    timeout=5s
    Input Text    id:cite_key    PublicRef2023
    Input Text    id:author      Another Author
    Input Text    id:title       Another Public Paper
    Input Text    id:journal     Test Journal
    Input Text    id:year        2023
    Click Button    id:save-reference-button
    Wait Until Location Contains    /all    timeout=15s
    Sleep    1s

Delete Test References For Public Private
    [Documentation]    Delete test references created for public/private tests
    Go To    ${BASE_URL}/all
    Sleep    1s

    # Delete public references (they are visible on /all page)
    FOR    ${ref_key}    IN    PublicRef2024    PublicRef2023
        ${exists}=    Run Keyword And Return Status    Page Should Contain Element    id:reference-item-${ref_key}
        IF    ${exists}
            ${button}=    Get WebElement    xpath://div[@id='reference-item-${ref_key}']//button[contains(text(), 'Poista')]
            Click Element    ${button}
            Handle Alert    ACCEPT
            Wait Until Page Does Not Contain Element    id:reference-item-${ref_key}    timeout=5s
            Sleep    0.5s
        END
    END

    # Delete private reference by accessing it directly via URL
    Go To    ${BASE_URL}/edit/PrivateRef2024
    ${exists}=    Run Keyword And Return Status    Page Should Contain Element    id:cite_key
    IF    ${exists}
        # Find and click delete button on edit page
        ${delete_exists}=    Run Keyword And Return Status    Page Should Contain Element    xpath://button[contains(text(), 'Poista')]
        IF    ${delete_exists}
            Click Element    xpath://button[contains(text(), 'Poista')]
            Handle Alert    ACCEPT
            Sleep    0.5s
        END
    END