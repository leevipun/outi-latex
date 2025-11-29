*** Settings ***
Documentation     User Story: User can filter and sort search results
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
