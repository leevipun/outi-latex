*** Settings ***
Documentation     User Story: As a user, I can see all added references
Library           SeleniumLibrary
Suite Setup       Open Browser    http://127.0.0.1:5001    chrome
Suite Teardown    Close Browser


*** Test Cases ***        
User Can See All Added References
    [Documentation]    Verify that the all references page displays all added references
    Go To    http://127.0.0.1:5001/all
    Page Should Contain    Tässä kaikki lisäämäsi viitteet
    Element Should Be Visible    xpath://a[contains(text(), 'Etusivu')]


User Can See Added Article Reference
    [Documentation]    Verify that an added article reference is displayed correctly
    Go To    http://127.0.0.1:5001/all
    Page Should Contain Element    xpath://div[@class='reference-item']
    Page Should Contain    TestArticle2024
    Page Should Contain    article
