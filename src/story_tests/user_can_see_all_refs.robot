*** Settings ***
Documentation     User Story: As a user, I can see all added references
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
User Can See All Added References
    [Documentation]    Verify that the all references page displays all added references
    Go To    ${BASE_URL}/all
    Page Should Contain Element    id:all-references-title
    Element Should Be Visible    id:back-to-home-button


User Can See Added Article Reference
    [Documentation]    Verify that an added article reference is displayed correctly
    [Setup]    Create Test Reference    TestArticle2024    John Doe    Sample Article Title    Journal of Testing    2024    10    2    100-110    Testing Publishers
    [Teardown]    Delete Test Reference    TestArticle2024

    Go To    ${BASE_URL}/all
    Page Should Contain Element    id:reference-item-TestArticle2024

User Can Delete Reference From All Page
    [Documentation]    User deletes an existing reference and it disappears from the list
    [Setup]    Create Test Reference    TestArticle2024    John Doe    Sample Article Title    Journal of Testing    2024    10    2    100-110    Testing Publishers
    [Teardown]    Run Keyword If Test Passed    Log    Reference already deleted

    Go To    ${BASE_URL}/all

    # Make sure the reference exists before deletion
    Page Should Contain Element    id:reference-item-TestArticle2024

    # Click the Poista button for that specific reference card
    Click Button    xpath=//div[@id="reference-item-TestArticle2024"]//button[normalize-space(.)="Poista"]

    # Confirm the JS confirm(...) dialog
    Handle Alert    ACCEPT

    Wait Until Page Contains Element    id:all-references-title    timeout=5s

    # After deletion, the reference card should be gone
    Page Should Not Contain Element    id:reference-item-TestArticle2024