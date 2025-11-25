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
    Wait Until Location Contains    /add?form=article
    Wait Until Element Is Visible   id:cite_key
    Input Text    id:cite_key    ${cite_key}
    Input Text    id:author      ${author}
    Input Text    id:title       ${title}
    Input Text    id:journal     ${journal}
    Input Text    id:year        ${year}
    Input Text    id:volume      ${volume}
    Input Text    id:number      ${number}
    Input Text    id:pages       ${pages}
    Input Text    id:publisher   ${publisher}
    Click Button    id:save-reference-button
    Wait Until Location Is    ${BASE_URL}/all

Create Two Test References
    Create Test Reference    TestArticle2024    John Doe    Sample Article Title    Journal of Testing    2024    10    2    100-110    Testing Publishers
    Create Test Reference    Kokeilu    Petri Nygård    Otsikko    Helsingin Yrittäjät    1995    40    21    67-420    Yritys Julkaisut

Delete Test Reference
    [Documentation]    Delete a test reference if it exists
    [Arguments]    ${cite_key}
    Go To    ${BASE_URL}/all
    ${exists}=    Run Keyword And Return Status    Page Should Contain Element    id:delete-button-${cite_key}
    IF    ${exists}
        Click Button    id:delete-button-${cite_key}
        Handle Alert    ACCEPT
        Wait Until Page Does Not Contain Element    id:reference-key-${cite_key}    timeout=5s
    END

Delete Two Test References
    Delete Test Reference    TestArticle2024
    Delete Test Reference    Kokeilu

*** Test Cases ***

User Can Access The Search Page
    [Documentation]    Verify that the search page is accessible and the user can get there
    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id:page-title
    Page Should Contain Element    id:search-form

User Can Type In The Search Field And Get Results
    [Documentation]    Verify that the search page has the search input and it is working
    [Setup]    Create Two Test References
    [Teardown]    Delete Two Test References

    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id:search-query
    Input Text    id:search-query    Test
    Click Button    id:search-button

    Wait Until Element Is Visible    id:reference-item-TestArticle2024
    Page Should Contain Element      id:reference-item-TestArticle2024

User Can Search With Author Name
    [Documentation]    Verify that searching by author works
    [Setup]    Create Two Test References
    [Teardown]    Delete Two Test References

    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id:search-query
    Input Text    id:search-query    Petri
    Click Button    id:search-button

    Wait Until Element Is Visible    id:reference-item-Kokeilu
    Page Should Contain Element      id:reference-item-Kokeilu

User Can Search With Title Keyword
    [Documentation]    Verify that searching by title works
    [Setup]    Create Two Test References
    [Teardown]    Delete Two Test References

    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id:search-query
    Input Text    id:search-query    Test
    Click Button    id:search-button

    Wait Until Element Is Visible    id:reference-item-TestArticle2024
    Page Should Contain Element      id:reference-item-TestArticle2024

User Can Search With Journal Name
    [Documentation]    Verify that searching by journal works
    [Setup]    Create Two Test References
    [Teardown]    Delete Two Test References

    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id:search-query
    Input Text    id:search-query    Helsingin
    Click Button    id:search-button

    Wait Until Element Is Visible    id:reference-item-Kokeilu
    Page Should Contain Element      id:reference-item-Kokeilu

User Can Search With Year
    [Documentation]    Verify that searching by year works
    [Setup]    Create Two Test References
    [Teardown]    Delete Two Test References

    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id:search-query
    Input Text    id:search-query    2024
    Click Button    id:search-button

    Wait Until Element Is Visible    id:reference-item-TestArticle2024
    Page Should Contain Element      id:reference-item-TestArticle2024