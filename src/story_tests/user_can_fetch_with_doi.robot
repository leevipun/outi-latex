*** Settings ***
Documentation     User Story: As a user, I can choose reference type (book, article...)
Library           SeleniumLibrary
Library           RequestsLibrary
Suite Setup       Initialize Test Environment
Suite Teardown    Close Browser

*** Keywords ***
Initialize Test Environment
    [Documentation]    Initialize the test environment
    Open Browser    ${BASE_URL}    chrome    options=add_argument("--headless");add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage");add_argument("--disable-gpu")

*** Test Cases ***        
User Can See DOI-button on home page
    [Documentation]    User selects "book" from dropdown and sees book form
    Go To    ${BASE_URL}
    Page Should Contain Element    id:add_doi-button
    Page Should Contain Element    id:doi-input
    