*** Settings ***
Documentation     User Story: As a user, I can see all added references
Library           SeleniumLibrary
Library           RequestsLibrary
Suite Setup       Initialize Test Environment
Suite Teardown    Close Browser

*** Keywords ***
Initialize Test Environment
    [Documentation]    Initialize the test environment
    Open Browser    ${BASE_URL}    chrome    options=add_argument("--headless");add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage");add_argument("--disable-gpu")

*** Test Cases ***        
User Can See All Added References
    [Documentation]    Verify that the all references page displays all added references
    Go To    ${BASE_URL}/all
    Page Should Contain Element    id:all-references-title
    Element Should Be Visible    id:back-to-home-button


User Can See Added Article Reference
    [Documentation]    Verify that an added article reference is displayed correctly
    Go To    ${BASE_URL}/all
    Page Should Contain Element    id:reference-item-TestArticle2024

User Can Delete Reference From All Page
    [Documentation]    User deletes an existing reference and it disappears from the list
    Go To    ${BASE_URL}/all

    # Make sure the reference exists before deletion
    Page Should Contain Element    id:reference-item-TestArticle2024

    # Click the Poista button for that specific reference card
    Click Button    xpath=//div[@id="reference-item-TestArticle2024"]//button[normalize-space(.)="Poista"]

    # Confirm the JS confirm(...) dialog
    Handle Alert    ACCEPT

    Sleep    1s

    # After deletion, the reference card should be gone
    Page Should Not Contain Element    id:reference-item-TestArticle2024