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
    Run Keyword And Continue On Failure    Page Should Contain Element    id:reference-key-${cite_key}
    Run Keyword And Continue On Failure    Click Button    id:delete-button-${cite_key}
    Handle Alert    ACCEPT
    Sleep    1s

*** Test Cases ***
User Can Access The Search Page
    [Documentation]    Verify that the search page is accessible and the user can get there
    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id:page-title
    Page Should Contain Element    id:search-form

User Can Type In The Search Field And Get Results
    [Documentation]    Verify that the search page has the search input and it is working
    [Setup]    Create Test Reference    TestArticle2024    John Doe    Sample Article Title    Journal of Testing    2024    10    2    100-110    Testing Publishers
    [Teardown]    Delete Test Reference    TestArticle2024

    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id:page-title
    Page Should Contain Element    id:search-query
    Input Text    id:search-query    Test
    Click Button    id:search-button
    Wait Until Element Is Visible    id:reference-item-TestArticle2024
    Page Should Contain Element    id:reference-item-TestArticle2024
