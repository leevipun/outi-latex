*** Settings ***
Documentation     User Story: As a user, I can export my references as BibTeX format
Library           SeleniumLibrary
Library           RequestsLibrary
Suite Setup       Initialize Test Environment
Suite Teardown    Cleanup Test Environment
Library           OperatingSystem
Library           String

*** Variables ***
${BASE_URL}       http://localhost:5001
${DOWNLOAD_DIR}     ${CURDIR}${/}downloads
${BIBTEX_FILE}      ${DOWNLOAD_DIR}${/}references.bib

*** Keywords ***
Initialize Test Environment
    [Documentation]    Initialize test environment with download directory

    # Luo downloads-kansio testeille
    Create Directory    ${DOWNLOAD_DIR}
    Empty Directory     ${DOWNLOAD_DIR}

    # Aseta Chrome lataamaan tiedostot downloads-kansioon
    ${chrome_options}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver
    ${prefs}=    Create Dictionary    download.default_directory=${DOWNLOAD_DIR}
    Call Method    ${chrome_options}    add_experimental_option    prefs    ${prefs}
    Call Method    ${chrome_options}    add_argument    --disable-popup-blocking

    Open Browser    ${BASE_URL}    Chrome    options=${chrome_options}
    Set Selenium Speed    0.2s
    Set Selenium Timeout    10s

Cleanup Test Environment
    [Documentation]    Clean up test environment
    Close Browser
    Remove Directory    ${DOWNLOAD_DIR}    recursive=True

Wait For Download
    [Documentation]    Wait for file to be downloaded
    [Arguments]    ${filename}    ${timeout}=10s

    FOR    ${i}    IN RANGE    20
        ${file_exists}=    Run Keyword And Return Status    File Should Exist    ${filename}
        Return From Keyword If    ${file_exists}
        Sleep    0.5s
    END
    Fail    File ${filename} was not downloaded within ${timeout}lenium Timeout    10s

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

Export Works With Multiple References
    [Documentation]    Verify that export works when multiple references exist
    Add Sample Article Reference
    Add Sample Book Reference

    Go To    ${BASE_URL}/all

    # Tarkista että molemmat viitteet näkyvät
    Page Should Contain Element    id:reference-item-TestArticle2023
    Page Should Contain Element    id:reference-item-TestBook2022

    Click Element    id:export-bibtex-button

    Page Should Not Contain    error

User Can Download And Verify BibTeX Content
    [Documentation]    Test downloading BibTeX file and verify its content
    Add Sample Article Reference

    Go To    ${BASE_URL}/all
    Click Element    id:export-bibtex-button

    # Odota että tiedosto latautuu
    Wait For Download    ${BIBTEX_FILE}

    # Lue tiedoston sisältö
    ${bibtex_content}=    Get File    ${BIBTEX_FILE}

    # Tarkista BibTeX-formaatti
    Should Contain    ${bibtex_content}    @article{TestArticle2023,
    Should Contain    ${bibtex_content}    author = {Test Author}
    Should Contain    ${bibtex_content}    title = {Test Article Title}
    Should Contain    ${bibtex_content}    journal = {Test Journal}
    Should Contain    ${bibtex_content}    year = {2023}
    Should Contain    ${bibtex_content}    volume = {42}

    Should Not Contain    ${bibtex_content}    ,${SPACE}${SPACE}${SPACE}${SPACE}}

BibTeX File Is Valid LaTeX Format
    [Documentation]    Test that generated BibTeX file follows valid LaTeX format
    Add Sample Article Reference

    Go To    ${BASE_URL}/all
    Click Element    id:export-bibtex-button

    Wait For Download    ${BIBTEX_FILE}
    ${bibtex_content}=    Get File    ${BIBTEX_FILE}

    # Tarkista BibTeX syntaksi
    Should Match Regexp    ${bibtex_content}    @\\w+\\{\\w+,

    # Tarkista että kentät on oikein formatoitu
    ${lines}=    Split To Lines    ${bibtex_content}
    FOR    ${line}    IN    @{lines}
        ${line}=    Strip String    ${line}
        Continue For Loop If    '${line}' == ''
        Continue For Loop If    '${line}' == '}'
        Continue For Loop If    '${line}'.startswith('@')

        # Jokaisen kentän pitää olla muodossa "key = {value},"
        Run Keyword If    '${line}' != '' and not '${line}'.startswith('@') and '${line}' != '}'
        ...    Should Match Regexp    ${line}    \\w+ = \\{.*\\},?
    END