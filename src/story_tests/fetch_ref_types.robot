*** Settings ***
Documentation     User Story: As a user, I can choose reference type (book, article...)
Library           SeleniumLibrary
Suite Setup       Open Browser    http://127.0.0.1:5001    chrome
Suite Teardown    Close Browser


*** Test Cases ***        
User Can See Available Reference Types
    [Documentation]    Verify that the index page displays all available reference types
    Go To    http://127.0.0.1:5001
    Page Should Contain    Hei! Lisää uusi Viite kirjastoosi!
    Element Should Be Visible    id:form
    Page Should Contain Element    xpath://select[@id='form']/option[contains(text(), 'book')]
    Page Should Contain Element    xpath://select[@id='form']/option[contains(text(), 'article')]
    Page Should Contain Element    xpath://select[@id='form']/option[contains(text(), 'inproceedings')]


User Can Select Book Reference Type
    [Documentation]    User selects "book" from dropdown and sees book form
    Go To    http://127.0.0.1:5001
    Select From List By Label    id:form    book
    Click Button    Lisää
    Location Should Contain    /add
    Location Should Contain    form=
    Page Should Contain    book
    Page Should Contain    author
    Page Should Contain    publisher


User Can Select Article Reference Type
    [Documentation]    User selects "article" from dropdown and sees article form
    Go To    http://127.0.0.1:5001
    Select From List By Label    id:form    article
    Click Button    Lisää
    Location Should Contain    /add
    Location Should Contain    form=
    Page Should Contain    article
    Page Should Contain    author
    Page Should Contain    journal


User Can Select Inproceedings Reference Type
    [Documentation]    User selects "inproceedings" and sees inproceedings form
    Go To    http://127.0.0.1:5001
    Select From List By Label    id:form    inproceedings
    Click Button    Lisää
    Location Should Contain    /add
    Location Should Contain    form=
    Page Should Contain    inproceedings
    Page Should Contain    author
    Page Should Contain    booktitle


Reference Type Form Has Correct Required Fields
    [Documentation]    Verify that each reference type has appropriate required fields
    Go To    http://127.0.0.1:5001
    
    # Test article form
    Select From List By Label    id:form    article
    Click Button    Lisää
    Element Should Be Visible    xpath://input[@id='author' and @required]
    Element Should Be Visible    xpath://input[@id='title' and @required]
    Element Should Be Visible    xpath://input[@id='journal' and @required]
    Element Should Be Visible    xpath://input[@id='year' and @required]


User Can Switch Between Reference Types
    [Documentation]    User can go back and select a different reference type
    Go To    http://127.0.0.1:5001
    Select From List By Label    id:form    article
    Click Button    Lisää
    Page Should Contain    article
    
    # Go back to home
    Click Link    Takaisin etusivulle
    Location Should Be    http://127.0.0.1:5001/
    
    # Select different type
    Select From List By Label    id:form    book
    Click Button    Lisää
    Page Should Contain    book
