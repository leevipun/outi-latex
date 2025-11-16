*** Settings ***
Documentation     User Story: As a user, I can see all added references
Library           SeleniumLibrary
Library           RequestsLibrary
Suite Setup       Initialize Test Environment
Suite Teardown    Close Browser

*** Keywords ***
Initialize Test Environment
    [Documentation]    Initialize the test environment by seeding database and opening browser
    ${response}=    GET    http://localhost:5001/reset_db    expected_status=200
    Sleep    1s
    Open Browser    ${BASE_URL}    chrome    options=add_argument("--headless");add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage");add_argument("--disable-gpu")
    # Add a test reference
    Go To    ${BASE_URL}
    Select From List By Label    id:form    article
    Click Button    + Lisää uusi viite
    Sleep    2s
    Input Text    id:cite_key    TestArticle2024
    Input Text    id:author    John Doe
    Input Text    id:title    Sample Article Title
    Input Text    id:journal    Journal of Testing
    Input Text    id:year    2024
    Click Button    Tallenna viite
    Sleep    2s

*** Test Cases ***        
User Can See All Added References
    [Documentation]    Verify that the all references page displays all added references
    Go To    ${BASE_URL}/all
    Page Should Contain    Tässä kaikki lisäämäsi viitteet
    Element Should Be Visible    xpath://a[contains(text(), 'Etusivu')]


User Can See Added Article Reference
    [Documentation]    Verify that an added article reference is displayed correctly
    Go To    ${BASE_URL}/all
    Page Should Contain Element    xpath://div[@class='reference-item']
    Page Should Contain    TestArticle2024
    Page Should Contain    article
