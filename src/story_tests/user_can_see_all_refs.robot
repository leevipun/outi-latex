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
