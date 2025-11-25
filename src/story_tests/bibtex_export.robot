*** Settings ***
Documentation     User Story: As a user, I can export my references as BibTeX format
Library           SeleniumLibrary
Library           RequestsLibrary
Suite Setup       Initialize Test Environment
Suite Teardown    Cleanup Test Environment
Library           OperatingSystem
Library           String
Library           DateTime

*** Variables ***
${BASE_URL}       http://localhost:5001
${TEST_TIMESTAMP}    ${EMPTY}

*** Keywords ***
Initialize Test Environment
    [Documentation]    Initialize test environment with unique test data

    # Luo uniikki timestamp jokaiselle test-ajokerralle
    ${timestamp}=    Get Current Date    result_format=%Y%m%d_%H%M%S_%f
    Set Suite Variable    ${TEST_TIMESTAMP}    ${timestamp}

    Open Browser    ${BASE_URL}    chrome    options=add_argument("--headless");add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage");add_argument("--disable-gpu")
    Set Selenium Speed    0.2s
    Set Selenium Timeout    10s

Cleanup Test Environment
    [Documentation]    Clean up test environment
    Close Browser

Delete Test Reference
    [Documentation]    Delete a test reference by its cite key
    [Arguments]    ${cite_key}
    Go To    ${BASE_URL}/all
    Run Keyword And Continue On Failure    Page Should Contain Element    id:reference-key-${cite_key}
    Run Keyword And Continue On Failure    Click Button    id:delete-button-${cite_key}
    Handle Alert    ACCEPT
    Sleep    1s

Add Sample Article Reference
    [Documentation]    Add a sample article reference for testing
    Go To    ${BASE_URL}

    Select From List By Value    id:form    article
    Click Button    id:add_new-button
    Sleep    2s

    Input Text       id:author        Test Author
    Input Text       id:title         Test Article Title
    Input Text       id:journal       Test Journal
    Input Text       id:year          2023
    Input Text       id:volume        42
    Input Text       id:cite_key      TestArticle_${TEST_TIMESTAMP}

    Click Button     id:save-reference-button
    Sleep    3s

Add Sample Book Reference
    [Documentation]    Add a sample book reference for testing
    Go To    ${BASE_URL}

    Select From List By Value    id:form    book
    Click Button    id:add_new-button
    Sleep    3s

    Wait Until Element Is Visible    id:author/editor    timeout=15s
    Input Text       id:author/editor    Book Author
    Input Text       id:title           Book Title
    Input Text       id:publisher       Test Publisher
    Input Text       id:year            2022
    Input Text       id:cite_key        TestBook_${TEST_TIMESTAMP}

    Click Button     id:save-reference-button
    Sleep    3s

*** Test Cases ***
User Can Access BibTeX Export Route
    [Documentation]    Verify that BibTeX export route is accessible
    Go To    ${BASE_URL}/export/bibtex
    Page Should Not Contain    404 Not Found
    Page Should Not Contain    500 Internal Server Error

User Can Export Empty BibTeX
    [Documentation]    Verify that empty BibTeX export works when no references exist
    Go To    ${BASE_URL}/export/bibtex
    ${current_url}=    Get Location
    Run Keyword If    '/all' in '${current_url}'
    ...    Page Should Not Contain    Database error

User Can See And Click Export Button When References Exist
    [Documentation]    Verify that export button appears on /all page when references exist
    [Setup]    Add Sample Article Reference
    [Teardown]    Delete Test Reference    TestArticle_${TEST_TIMESTAMP}

    Go To    ${BASE_URL}/all
    Page Should Contain Element    id:all-references-title

    Page Should Contain Element    id:export-bibtex-button
    Click Element                  id:export-bibtex-button

    Page Should Not Contain    Database error
    Page Should Not Contain    Export error
    Page Should Not Contain    500 Internal Server Error

Export Works With Multiple References
    [Documentation]    Verify that export works when multiple references exist
    [Setup]    Run Keywords    Add Sample Article Reference    AND    Add Sample Book Reference
    [Teardown]    Run Keywords    Delete Test Reference    TestArticle_${TEST_TIMESTAMP}    AND    Delete Test Reference    TestBook_${TEST_TIMESTAMP}

    Go To    ${BASE_URL}/all
    Sleep    2s

    Wait Until Page Contains Element    id:reference-item-TestArticle_${TEST_TIMESTAMP}    timeout=15s
    Wait Until Page Contains Element    id:reference-item-TestBook_${TEST_TIMESTAMP}    timeout=15s

    Wait Until Page Contains Element    id:export-bibtex-button    timeout=10s
    Click Element    id:export-bibtex-button

    Page Should Not Contain    error

User Can Download And Verify BibTeX Content
    [Documentation]    Test BibTeX content via HTTP
    [Setup]    Add Sample Article Reference
    [Teardown]    Delete Test Reference    TestArticle_${TEST_TIMESTAMP}

    Create Session    api    ${BASE_URL}
    ${response}=    GET On Session    api    /export/bibtex

    Should Be Equal As Numbers    ${response.status_code}    200

    # Tarkista BibTeX sisältö - käytä uniikkia cite_key:tä
    ${bibtex_content}=    Set Variable    ${response.text}
    Should Contain    ${bibtex_content}    @article{TestArticle_${TEST_TIMESTAMP},
    Should Contain    ${bibtex_content}    author = {Test Author}
    Should Contain    ${bibtex_content}    title = {Test Article Title}
    Should Contain    ${bibtex_content}    journal = {Test Journal}
    Should Contain    ${bibtex_content}    year = {2023}
    Should Contain    ${bibtex_content}    volume = {42}

BibTeX Content Is Valid LaTeX Format
    [Documentation]    Test BibTeX format via HTTP - basic validation
    [Setup]    Add Sample Article Reference
    [Teardown]    Delete Test Reference    TestArticle_${TEST_TIMESTAMP}

    Create Session    api    ${BASE_URL}
    ${response}=    GET On Session    api    /export/bibtex
    ${bibtex_content}=    Set Variable    ${response.text}

    Should Contain    ${bibtex_content}    @article{TestArticle_${TEST_TIMESTAMP},
    Should Contain    ${bibtex_content}    author = {Test Author}
    Should Contain    ${bibtex_content}    title = {Test Article Title}
    Should Contain    ${bibtex_content}    journal = {Test Journal}
    Should Contain    ${bibtex_content}    year = {2023}

    # Tarkista että alkaa @ merkillä
    Should Match Regexp    ${bibtex_content}    ^@\\w+\\{

    # Tarkista että päättyy } merkkiin
    Should Match Regexp    ${bibtex_content}    \\}\\s*$

    # Tarkista että ei ole tyhjiä kenttiä
    Should Not Contain    ${bibtex_content}    = {}
    Should Not Contain    ${bibtex_content}    = {$EMPTY}
