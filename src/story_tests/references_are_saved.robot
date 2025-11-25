*** Settings ***
Documentation     User Story: As a user, I can save a reference
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
    Run Keyword And Continue On Failure    Page Should Contain Element    id:reference-key-${cite_key}
    Run Keyword And Continue On Failure    Click Button    id:delete-button-${cite_key}
    Handle Alert    ACCEPT
    Sleep    1s

*** Test Cases ***
User Can Save Reference
    [Documentation]    Verify that a user can save a reference and it is stored correctly
    [Teardown]    Delete Test Reference    TestArticle2024

    Go To    ${BASE_URL}
    Select From List By Value    id:form    article
    Click Button    id:add_new-button
    Sleep    2s
    Location Should Contain    ${BASE_URL}/add?form=article
    Input Text    id:cite_key    TestArticle2024
    Input Text    id:author    John Doe
    Input Text    id:title    Sample Article Title
    Input Text    id:journal    Journal of Testing
    Input Text    id:year    2024
    Input Text    id:volume    10
    Input Text    id:number    2
    Input Text    id:pages    100-110
    Input Text    id:publisher    Testing Publishers
    Click Button    id:save-reference-button
    Sleep    2s
    Location Should Be    ${BASE_URL}/all
    Page Should Contain Element    id:all-references-title
