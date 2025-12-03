*** Settings ***
Documentation     User Story: As a user, I can filter and sort search results
Library           SeleniumLibrary
Library           RequestsLibrary
Suite Setup       Initialize Test Environment And Create Test Data
Suite Teardown    Clean Up Test Data And Close Browser

*** Variables ***
${BASE_URL}       http://localhost:5001

*** Keywords ***
Initialize Test Environment And Create Test Data
    [Documentation]    Initialize the test environment and create test data once for all tests
    Open Browser    ${BASE_URL}    chrome    options=add_argument("--headless");add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage");add_argument("--disable-gpu")
    Create Test References For Filtering

Clean Up Test Data And Close Browser
    [Documentation]    Clean up test data and close browser after all tests
    Delete Test References For Filtering
    Close Browser

Create Test References For Filtering
    [Documentation]    Create multiple test references for filtering tests
    Go To    ${BASE_URL}
    
    # Create first article reference
    Select From List By Value    id:form    article
    Click Button    id:add_new-button
    Wait Until Location Contains    /add?form=article    timeout=10s
    Wait Until Element Is Visible   id:cite_key    timeout=5s
    Input Text    id:cite_key    Article2024
    Input Text    id:author      Smith John
    Input Text    id:title       Modern Testing Approaches
    Input Text    id:journal     Journal of Software Testing
    Input Text    id:year        2024
    Input Text    id:volume      15
    Input Text    id:number      3
    Input Text    id:pages       45-62
    Click Button    id:save-reference-button
    Wait Until Location Contains    /all    timeout=15s
    Sleep    1s
    
    # Create second article reference
    Go To    ${BASE_URL}
    Sleep    1s
    Select From List By Value    id:form    article
    Click Button    id:add_new-button
    Wait Until Location Contains    /add?form=article    timeout=10s
    Wait Until Element Is Visible   id:cite_key    timeout=5s
    Input Text    id:cite_key    Article2023
    Input Text    id:author      Brown Michael
    Input Text    id:title       Legacy Systems in Testing
    Input Text    id:journal     Journal of Legacy Code
    Input Text    id:year        2023
    Input Text    id:volume      10
    Input Text    id:number      2
    Input Text    id:pages       20-35
    Click Button    id:save-reference-button
    Wait Until Location Contains    /all    timeout=15s
    Sleep    1s
    
    # Create book reference
    Go To    ${BASE_URL}
    Sleep    1s
    Select From List By Value    id:form    book
    Click Button    id:add_new-button
    Wait Until Location Contains    /add?form=book    timeout=10s
    Wait Until Element Is Visible   id:cite_key    timeout=5s
    Input Text    id:cite_key    Book2024
    Input Text    id:author/editor      Green Alice
    Input Text    id:title       The Testing Bible
    Input Text    id:year        2024
    Input Text    id:publisher   Test Publications
    Click Button    id:save-reference-button
    Wait Until Location Contains    /all    timeout=15s
    Sleep    1s

Delete Test References For Filtering
    [Documentation]    Delete test references created for filtering tests
    Go To    ${BASE_URL}/all
    Sleep    1s
    
    # Delete each reference - find delete button by its form action
    FOR    ${ref_key}    IN    Article2024    Article2023    Book2024
        ${exists}=    Run Keyword And Return Status    Page Should Contain Element    id:reference-item-${ref_key}
        IF    ${exists}
            # Find the delete button within this reference item and click it
            ${button}=    Get WebElement    xpath://div[@id='reference-item-${ref_key}']//button[contains(text(), 'Poista')]
            Click Element    ${button}
            Handle Alert    ACCEPT
            Wait Until Page Does Not Contain Element    id:reference-item-${ref_key}    timeout=5s
            Sleep    0.5s
        END
    END

*** Test Cases ***

User Can Access Search Page With Filter Controls
    [Documentation]    Verify that search page displays all filter controls
    Go To    ${BASE_URL}/search
    
    Wait Until Element Is Visible    id:search-form
    Page Should Contain Element    id:search-query
    Page Should Contain Element    id:search-button
    Page Should Contain Element    id:filter-type
    Page Should Contain Element    id:tag-filter
    Page Should Contain Element    id:sort-by

User Can Filter Search Results By Reference Type
    [Documentation]    Verify that filtering by reference type works
    
    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id:filter-type
    
    # Filter by article type
    Select From List By Value    id:filter-type    article
    Click Button    id:search-button
    
    Wait Until Element Is Visible    id:reference-item-Article2024    timeout=5s
    Page Should Contain Element    id:reference-item-Article2024
    Page Should Contain Element    id:reference-item-Article2023
    Page Should Not Contain Element    id:reference-item-Book2024

User Can Filter Search Results By Type Book
    [Documentation]    Verify that filtering by book type works
    
    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id:filter-type
    
    # Filter by book type
    Select From List By Value    id:filter-type    book
    Click Button    id:search-button
    
    Wait Until Element Is Visible    id:reference-item-Book2024    timeout=5s
    Page Should Contain Element    id:reference-item-Book2024
    Page Should Not Contain Element    id:reference-item-Article2024

User Can Clear Type Filter To See All References
    [Documentation]    Verify that selecting empty option shows all references
    
    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id:filter-type    timeout=5s
    
    # First filter by article
    Select From List By Value    id:filter-type    article
    Click Button    id:search-button
    Wait Until Element Is Visible    id:reference-item-Article2024    timeout=5s
    
    # Then clear filter
    Select From List By Value    id:filter-type    ${EMPTY}
    Click Button    id:search-button
    
    Wait Until Element Is Visible    id:reference-item-Article2024    timeout=5s
    Wait Until Element Is Visible    id:reference-item-Article2023    timeout=5s
    Wait Until Element Is Visible    id:reference-item-Book2024    timeout=5s
    Page Should Contain Element    id:reference-item-Article2024
    Page Should Contain Element    id:reference-item-Article2023
    Page Should Contain Element    id:reference-item-Book2024

User Can Sort Search Results By Oldest First
    [Documentation]    Verify that sorting by oldest first works
    
    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id:sort-by    timeout=5s
    
    Select From List By Value    id:sort-by    oldest
    Click Button    id:search-button
    
    Wait Until Element Is Visible    id:reference-item-Article2023    timeout=5s
    Page Should Contain Element    id:reference-item-Article2023

User Can Sort Search Results By Bib Key Alphabetically
    [Documentation]    Verify that sorting by bib_key (A-Ö) works
    
    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id:sort-by    timeout=5s
    
    Select From List By Value    id:sort-by    bib_key
    Click Button    id:search-button
    
    Wait Until Element Is Visible    id:reference-key-Article2023    timeout=5s
    Page Should Contain Element    id:reference-key-Article2023

User Can Sort Search Results By Title Alphabetically
    [Documentation]    Verify that sorting by title (A-Ö) works
    
    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id:sort-by    timeout=5s
    
    Select From List By Value    id:sort-by    title
    Click Button    id:search-button
    
    Wait Until Element Is Visible    id:search-results-heading    timeout=5s
    Page Should Contain Element    id:reference-item-Article2024

User Can Sort Search Results By Author Alphabetically
    [Documentation]    Verify that sorting by author (A-Ö) works
    
    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id:sort-by    timeout=5s
    
    Select From List By Value    id:sort-by    author
    Click Button    id:search-button
    
    Wait Until Element Is Visible    id:search-results-heading    timeout=5s
    Page Should Contain Element    id:reference-item-Article2024

User Can Combine Multiple Filters
    [Documentation]    Verify that combining filter type and sort works
    
    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id:filter-type    timeout=5s
    Wait Until Element Is Visible    id:sort-by    timeout=5s
    
    # Filter by article AND sort by newest
    Select From List By Value    id:filter-type    article
    Select From List By Value    id:sort-by    newest
    Click Button    id:search-button
    
    Wait Until Element Is Visible    id:reference-item-Article2024    timeout=5s
    Page Should Contain Element    id:reference-item-Article2024
    Page Should Contain Element    id:reference-item-Article2023
    Page Should Not Contain Element    id:reference-item-Book2024

User Can Edit Reference From Search Results
    [Documentation]    Verify that user can click edit button from search results
    
    Go To    ${BASE_URL}/search
    Input Text    id:search-query    Testing
    Click Button    id:search-button
    
    Wait Until Element Is Visible    id:edit-button-Article2024    timeout=5s
    Click Button    id:edit-button-Article2024
    Wait Until Location Contains    /edit/    timeout=10s
    Page Should Contain Element    id:cite_key

User Can Delete Reference From Search Results
    [Documentation]    Verify that user can see delete button from search results
    
    Go To    ${BASE_URL}/search
    Input Text    id:search-query    ${EMPTY}
    Click Button    id:search-button
    
    Wait Until Element Is Visible    id:reference-item-Article2024    timeout=5s
    # Verify delete button is present
    Wait Until Element Is Visible    xpath://div[@id='reference-item-Article2024']//button[contains(text(), 'Poista')]    timeout=5s
    Page Should Contain Element    id:reference-item-Article2024

No Results Message Is Displayed For Empty Search
    [Documentation]    Verify that no results message appears when search finds nothing
    
    Go To    ${BASE_URL}/search
    Input Text    id:search-query    XyZ123NoResultsZyx
    Click Button    id:search-button
    
    Wait Until Element Is Visible    id:no-results-div    timeout=5s
    Page Should Contain Element    id:no-results-message
    Page Should Contain    Ei hakutuloksia.

User Can Navigate Back To Home From Search Results
    [Documentation]    Verify that back to home button works
    
    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id:back-to-home-button    timeout=5s
    Click Element    id:back-to-home-button
    
    Wait Until Location Contains    /    timeout=10s
    Page Should Contain Element    id:page-title