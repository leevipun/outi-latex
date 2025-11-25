*** Settings ***
Documentation     User Story: As a user, I can choose reference type (book, article...)
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

*** Test Cases ***
User Can Select Book Reference Type
    [Documentation]    User selects "book" from dropdown and sees book form
    Go To    ${BASE_URL}
    Select From List By Value    id:form    book
    Click Button    id:add_new-button
    Wait Until Page Contains Element    id:reference-type-heading    timeout=5s
    Location Should Contain    /add
    Page Should Contain Element    id:reference-type-heading
    Page Should Contain Element    id:author/editor
    Page Should Contain Element    id:publisher


User Can Select Article Reference Type
    [Documentation]    User selects "article" from dropdown and sees article form
    Go To    ${BASE_URL}
    Select From List By Value    id:form    article
    Click Button    id:add_new-button
    Wait Until Page Contains Element    id:reference-type-heading    timeout=5s
    Location Should Contain    /add
    Page Should Contain Element    id:reference-type-heading
    Page Should Contain Element    id:author
    Page Should Contain Element    id:journal


User Can Select Inproceedings Reference Type
    [Documentation]    User selects "inproceedings" and sees inproceedings form
    Go To    ${BASE_URL}
    Select From List By Value    id:form    inproceedings
    Click Button    id:add_new-button
    Wait Until Page Contains Element    id:reference-type-heading    timeout=5s
    Location Should Contain    /add
    Page Should Contain Element    id:reference-type-heading
    Page Should Contain Element    id:author
    Page Should Contain Element    id:booktitle


User Can Switch Between Reference Types
    [Documentation]    User can go back and select a different reference type
    Go To    ${BASE_URL}
    Select From List By Value    id:form    article
    Click Button    id:add_new-button
    Wait Until Page Contains Element    id:reference-type-heading    timeout=5s
    # Page Should Contain Element    id:reference-type-heading

    # Go back to home
    Click Link    id:back-to-home
    Wait Until Page Contains Element    id:reference-type-form    timeout=5s
    Location Should Be    ${BASE_URL}/

    # Select different type
    Select From List By Value    id:form    book
    Click Button    id:add_new-button
    Wait Until Page Contains Element    id:reference-type-heading    timeout=5s
