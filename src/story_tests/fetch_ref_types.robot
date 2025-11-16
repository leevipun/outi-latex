*** Settings ***
Documentation     User Story: As a user, I can choose reference type (book, article...)
Library           SeleniumLibrary
Suite Setup       Open Browser    ${BASE_URL}    chrome    options=add_argument("--headless");add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage");add_argument("--disable-gpu")
Suite Teardown    Close Browser

*** Test Cases ***        
User Can Select Book Reference Type
    [Documentation]    User selects "book" from dropdown and sees book form
    Go To    ${BASE_URL}
    Select From List By Label    id:form    book
    Click Button    id:add_new-button
    Sleep    2s
    Location Should Contain    /add
    Location Should Contain    form=book
    Page Should Contain    book -viite
    Page Should Contain    Lisää uusi viite
    Page Should Contain Element    id:author/editor
    Page Should Contain Element    id:publisher


User Can Select Article Reference Type
    [Documentation]    User selects "article" from dropdown and sees article form
    Go To    ${BASE_URL}
    Select From List By Label    id:form    article
    Click Button    + Lisää uusi viite
    Sleep    2s
    Location Should Contain    /add
    Location Should Contain    form=article
    Page Should Contain    article -viite
    Page Should Contain Element    id:author
    Page Should Contain Element    id:journal


User Can Select Inproceedings Reference Type
    [Documentation]    User selects "inproceedings" and sees inproceedings form
    Go To    ${BASE_URL}
    Select From List By Label    id:form    inproceedings
    Click Button    + Lisää uusi viite
    Sleep    2s
    Location Should Contain    /add
    Location Should Contain    form=inproceedings
    Page Should Contain    inproceedings -viite
    Page Should Contain Element    id:author
    Page Should Contain Element    id:booktitle


User Can Switch Between Reference Types
    [Documentation]    User can go back and select a different reference type
    Go To    ${BASE_URL}
    Select From List By Label    id:form    article
    Click Button    + Lisää uusi viite
    Sleep    2s
    Page Should Contain    article -viite
    
    # Go back to home
    Click Link    ← Takaisin etusivulle
    Sleep    2s
    Location Should Be    ${BASE_URL}/
    
    # Select different type
    Select From List By Label    id:form    book
    Click Button    + Lisää uusi viite
    Sleep    2s
    Page Should Contain    book -viite
