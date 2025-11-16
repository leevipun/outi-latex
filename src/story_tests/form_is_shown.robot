*** Settings ***
Documentation     User Story: As a user, I see the right form
Library           SeleniumLibrary
Suite Setup       Open Browser    ${BASE_URL}    chrome    options=add_argument("--headless");add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage");add_argument("--disable-gpu")
Suite Teardown    Close Browser

*** Test Cases ***
User Sees Form After Selecting Reference Type
    [Documentation]    Verify that selecting a reference type displays the correct form
    Go To    ${BASE_URL}
    Select From List By Label    id:form    article
    Click Button    + Lisää uusi viite
    Sleep    2s
    Location Should Contain    ${BASE_URL}/add
    Location Should Contain    form=article
    Page Should Contain    Lisää uusi viite
    Page Should Contain    article -viite
    Page Should Contain Element    id:author
    Page Should Contain Element    id:cite_key
    Go Back

User Sees Right Input Fields For Article
    [Documentation]    Verify that the article form has the correct input fields
    Go To    ${BASE_URL}/add?form=article
    Page Should Contain Element    id:cite_key
    Page Should Contain Element    id:author
    Page Should Contain Element    id:title
    Page Should Contain Element    id:journal
    Page Should Contain Element    id:year
    Page Should Contain Element    id:volume
    Page Should Contain Element    id:number
    Page Should Contain Element    id:pages
    Page Should Contain Element    id:doi
    Page Should Contain Element    id:publisher