*** Settings ***
Documentation     User Story: As a user, I can edit my added references
Library           SeleniumLibrary
Library           RequestsLibrary
Suite Setup       Initialize Test Environment
Suite Teardown    Close Browser

*** Keywords ***
Initialize Test Environment
    [Documentation]    Initialize the test environment
    Open Browser    ${BASE_URL}    chrome    options=add_argument("--headless");add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage");add_argument("--disable-gpu")

*** Test Cases ***
User Can Edit A Reference
    [Documentation]    Verify that an added reference changes upon edit

    Go To    ${BASE_URL}
    Select From List By Value    id:form    article
    Click Button    id:add_new-button
    Sleep    2s
    Location Should Contain    ${BASE_URL}/add?form=article
    Input Text    id:cite_key    EditableArticle
    Input Text    id:author    John Snow
    Input Text    id:title    Title
    Input Text    id:journal    Journal
    Input Text    id:year    2002
    Input Text    id:volume    9
    Input Text    id:number    2
    Input Text    id:pages    2-4
    Input Text    id:publisher    Publisher
    Click Button    id:save-reference-button
    Sleep    2s
    Location Should Be    ${BASE_URL}/all
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

