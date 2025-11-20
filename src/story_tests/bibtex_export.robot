*** Settings ***
Documentation     User Story: As a user, I can export my references as BibTeX format
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
    Input Text       id:cite_key      TestArticle2023

    Click Button     id:save-reference-button

Add Sample Book Reference
    [Documentation]    Add a sample book reference for testing
    Go To    ${BASE_URL}

    Select From List By Value    id:form    book
    Click Button    id:add_new-button
    Sleep    2s

    Input Text       id:author/editor    Book Author
    Input Text       id:title           Book Title
    Input Text       id:publisher       Test Publisher
    Input Text       id:year            2022
    Input Text       id:cite_key        TestBook2022

    Click Button     id:save-reference-button

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
    Add Sample Article Reference

    Go To    ${BASE_URL}/all
    Page Should Contain Element    id:all-references-title

    Page Should Contain Element    id:export-bibtex-button
    Click Element                  id:export-bibtex-button

    Page Should Not Contain    Database error
    Page Should Not Contain    Export error
    Page Should Not Contain    500 Internal Server Error
