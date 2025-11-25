*** Settings ***
Documentation     User Story: As a user, I can fetch a reference with DOI
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
    Set Selenium Implicit Wait    10s

*** Test Cases ***
User Can See DOI-button on home page
    [Documentation]    User sees DOI input and fetch button on home page
    Go To    ${BASE_URL}
    Wait Until Element Is Visible    id:add_doi-button    timeout=10s
    Wait Until Element Is Visible    id:doi-input    timeout=10s
    Page Should Contain Element    id:add_doi-button
    Page Should Contain Element    id:doi-input

User Can Fetch with DOI
    [Documentation]    User enters DOI and clicks fetch button, sees pre-filled form with values

    Go To    ${BASE_URL}
    Wait Until Element Is Visible    id:doi-input    timeout=10s
    Input Text    id:doi-input    10.1145/2783446.2783605
    Click Button    id:add_doi-button
    Wait Until Element Is Visible    id:add-reference-title    timeout=30s
    Wait Until Element Is Visible    id:author    timeout=30s
    Textfield Value Should Be    id:author    Kristian Garza, Carole Goble, John Brooke, Caroline Jay
    Textfield Value Should Be    id:title    Framing the community data system interface
    Textfield Value Should Be    id:booktitle    Proceedings of the 2015 British HCI Conference
    Textfield Value Should Be    id:year    2015
    Textfield Value Should Be    id:pages    269-270
    Textfield Value Should Be    id:publisher    ACM
    Textfield Value Should Be    id:month    7
    Textfield Value Should Be    id:doi    10.1145/2783446.2783605

User Sees Error on Invalid DOI
    [Documentation]    User enters invalid DOI and sees error message
    Go To    ${BASE_URL}
    Wait Until Element Is Visible    id:doi-input    timeout=10s
    Input Text    id:doi-input    invalid_doi_12345
    Click Button    id:add_doi-button
    Wait Until Element Is Visible    id:alert-error    timeout=10s
    Page Should Contain Element    id:alert-error