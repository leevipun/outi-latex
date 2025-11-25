*** Settings ***
Documentation     User Story: As a user, I can edit my added references
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
    Page Should Contain Element    id:reference-key-${cite_key}
    Click Button    id:delete-button-${cite_key}
    Handle Alert    ACCEPT
    Sleep    1s
    Page Should Not Contain Element    id:reference-key-${cite_key}

*** Test Cases ***
User Can Edit A Reference
    [Documentation]    Verify that an added reference changes upon edit
    [Setup]    Create Test Reference    EditableArticle    John Snow    Title    Journal    2002    9    2    2-4    Publisher
    [Teardown]    Delete Test Reference    EditableArticle

    Go To    ${BASE_URL}/all
    Page Should Contain Element    id:reference-key-EditableArticle
    Element Text Should Be    id:value-EditableArticle-year    2002
    Click Button    id:edit-button-EditableArticle
    Sleep    2s
    Location Should Contain    ${BASE_URL}/edit/EditableArticle?
    Input Text    id:author    John Lennon
    Input Text    id:title    Edited Title
    Input Text    id:journal    Edited Journal
    Input Text    id:year    1984
    Input Text    id:volume    8
    Input Text    id:number    3
    Input Text    id:pages    1-5
    Input Text    id:publisher    Edited Publisher
    Click Button    id:save-reference-button
    Sleep    2s
    Location Should Contain    ${BASE_URL}/all
    Page Should Contain Element    id:reference-key-EditableArticle
    Element Text Should Be    id:value-EditableArticle-author    John Lennon
    Element Text Should Be    id:value-EditableArticle-journal    Edited Journal
    Element Text Should Be    id:value-EditableArticle-number    3
    Element Text Should Be    id:value-EditableArticle-pages    1-5
    Element Text Should Be    id:value-EditableArticle-title    Edited Title
    Element Text Should Be    id:value-EditableArticle-volume    8
    Element Text Should Be    id:value-EditableArticle-year    1984

User Can Edit Reference Bibkey
    [Documentation]    Verify that reference's bib key can be changed
    [Setup]    Create Test Reference    EditableArticle    John Lennon    Edited Title    Edited Journal    1984    8    3    1-5    Edited Publisher
    [Teardown]    Delete Test Reference    EditedArticle

    Go To    ${BASE_URL}/all
    Page Should Contain Element    id:reference-key-EditableArticle
    Element Text Should Be    id:value-EditableArticle-year    1984
    Click Button    id:edit-button-EditableArticle
    Sleep    2s
    Location Should Contain    ${BASE_URL}/edit/EditableArticle?
    Input Text    id:cite_key    EditedArticle
    Click Button    id:save-reference-button
    Sleep    2s
    Location Should Contain    ${BASE_URL}/all
    Page Should Not Contain Element    id:reference-key-EditableArticle
    Page Should Contain Element    id:reference-key-EditedArticle
    Element Text Should Be    id:value-EditedArticle-author    John Lennon

