*** Settings ***
Documentation     User Story: User can filter and sort search results
Library           SeleniumLibrary
Library           RequestsLibrary
Suite Setup       Initialize Test Environment
Suite Teardown    Close Browser

*** Variables ***
${BASE_URL}       http://localhost:5001

*** Keywords ***
Initialize Test Environment
    [Documentation]    Initialize the test environment and add test data
    Open Browser    ${BASE_URL}    chrome    options=add_argument("--headless");add_argument("--no-sandbox");add_argument("--disable-dev-shm-usage");add_argument("--disable-gpu")
    Add Test References With Tags

Add Test References With Tags
    [Documentation]    Add multiple test references with different tags for filtering and sorting tests
    Add Sample Article Reference
    Add Sample Book Reference
    Add Sample Inproceedings Reference
    Add Another Article Reference

Add Sample Article Reference
    [Documentation]    Add a sample article reference for testing
    Go To    ${BASE_URL}
    Select From List By Value    id:form    article
    Click Button    id:add_new-button
    Wait Until Element Is Visible    id:author    timeout=15s
    Input Text       id:author        Smith, John
    Input Text       id:title         Advanced Machine Learning
    Input Text       id:journal       AI Journal
    Input Text       id:year          2020
    Input Text       id:volume        42
    Input Text       id:cite_key      Smith2020
    Input Text       id:new_tag       machine-learning
    Click Button     id:save-reference-button
    Wait Until Page Contains    Smith2020    timeout=10s

Add Sample Book Reference
    [Documentation]    Add a sample book reference for testing
    Go To    ${BASE_URL}
    Select From List By Value    id:form    book
    Click Button    id:add_new-button
    Wait Until Element Is Visible    id:author/editor    timeout=15s
    Input Text       id:author/editor    Anderson, James
    Input Text       id:title           Data Structures
    Input Text       id:publisher       Tech Press
    Input Text       id:year            2021
    Input Text       id:cite_key        Anderson2021
    Input Text       id:new_tag         algorithms
    Click Button     id:save-reference-button
    Wait Until Page Contains    Anderson2021    timeout=10s

Add Sample Inproceedings Reference
    [Documentation]    Add a sample Inproceedings reference for testing
    Go To    ${BASE_URL}
    Select From List By Value    id:form    inproceedings
    Click Button    id:add_new-button
    Wait Until Element Is Visible    id:author    timeout=15s
    Input Text       id:author        Johnson, Mary
    Input Text       id:title         Big Data Analytics
    Input Text       id:booktitle     Conference Proceedings
    Input Text       id:year          2019
    Input Text       id:cite_key      Johnson2019
    Input Text       id:new_tag       data-science
    Click Button     id:save-reference-button
    Wait Until Page Contains    Johnson2019    timeout=10s

Add Another Article Reference
    [Documentation]    Add another article reference for testing
    Go To    ${BASE_URL}
    Select From List By Value    id:form    article
    Click Button    id:add_new-button
    Wait Until Element Is Visible    id:author    timeout=15s
    Input Text       id:author        Brown, Alice
    Input Text       id:title         Cloud Computing Basics
    Input Text       id:journal       Tech Journal
    Input Text       id:year          2022
    Input Text       id:volume        10
    Input Text       id:cite_key      Brown2022
    Input Text       id:new_tag       machine-learning
    Click Button     id:save-reference-button
    Wait Until Page Contains    Brown2022    timeout=10s

*** Test Cases ***
User Can Filter Search Results By Reference Type
    [Documentation]    User can filter search results by reference type
    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id=search-button    timeout=10s
    Click Button    id=search-button
    Wait Until Page Contains Element    id=filter-type    timeout=10s
    Select From List By Label    id=filter-type    Article
    Click Button    id=search-button
    Wait Until Page Contains    Smith, John    timeout=10s
    Page Should Contain    Brown, Alice
    Page Should Not Contain    Anderson, James
    Page Should Not Contain    Johnson, Mary

User Can Filter Search Results By Tag
    [Documentation]    User can filter search results by tag
    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id=search-button    timeout=10s
    Click Button    id=search-button
    Wait Until Page Contains Element    id=tag-filter    timeout=10s
    Select From List By Label    id=tag-filter    machine-learning
    Click Button    id=search-button
    Wait Until Page Contains    Smith, John    timeout=10s
    Page Should Contain    Brown, Alice
    Page Should Not Contain    Anderson, James

User Can Sort Search Results By Newest First
    [Documentation]    User can sort search results by newest added first (created_at)
    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id=search-button    timeout=10s
    Click Button    id=search-button
    Wait Until Page Contains Element    id=sort-by    timeout=10s
    Select From List By Value    id=sort-by    newest
    Click Button    id=search-button
    Wait Until Page Contains    Brown2022    timeout=10s
    ${page_text}=    Get Text    css=body
    ${pos_brown}=    Evaluate    $page_text.find('Brown2022')
    ${pos_smith}=    Evaluate    $page_text.find('Smith2020')
    Should Be True    ${pos_brown} < ${pos_smith}

User Can Sort Search Results By Oldest First
    [Documentation]    User can sort search results by oldest added first (created_at)
    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id=search-button    timeout=10s
    Click Button    id=search-button
    Wait Until Page Contains Element    id=sort-by    timeout=10s
    Select From List By Value    id=sort-by    oldest
    Click Button    id=search-button
    Wait Until Page Contains    Smith2020    timeout=10s
    ${page_text}=    Get Text    css=body
    ${pos_smith}=    Evaluate    $page_text.find('Smith2020')
    ${pos_brown}=    Evaluate    $page_text.find('Brown2022')
    Should Be True    ${pos_smith} < ${pos_brown}

User Can Sort Search Results By Author
    [Documentation]    User can sort search results alphabetically by author
    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id=search-button    timeout=10s
    Click Button    id=search-button
    Wait Until Page Contains Element    id=sort-by    timeout=10s
    Select From List By Value    id=sort-by    author
    Click Button    id=search-button
    Wait Until Page Contains    Anderson    timeout=10s
    ${page_text}=    Get Text    css=body
    ${pos_anderson}=    Evaluate    $page_text.find('Anderson')
    ${pos_smith}=    Evaluate    $page_text.find('Smith')
    Should Be True    ${pos_anderson} < ${pos_smith}

User Can Sort Search Results By Title
    [Documentation]    User can sort search results alphabetically by title
    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id=search-button    timeout=10s
    Click Button    id=search-button
    Wait Until Page Contains Element    id=sort-by    timeout=10s
    Select From List By Value    id=sort-by    title
    Click Button    id=search-button
    Wait Until Page Contains    Advanced    timeout=10s
    ${page_text}=    Get Text    css=body
    ${pos_advanced}=    Evaluate    $page_text.find('Advanced')
    ${pos_data}=    Evaluate    $page_text.find('Data Structures')
    Should Be True    ${pos_advanced} < ${pos_data}

User Can Sort Search Results By Bib Key
    [Documentation]    User can sort search results alphabetically by bib_key
    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id=search-button    timeout=10s
    Click Button    id=search-button
    Wait Until Page Contains Element    id=sort-by    timeout=10s
    Select From List By Value    id=sort-by    bib_key
    Click Button    id=search-button
    Wait Until Page Contains    Anderson2021    timeout=10s
    ${page_text}=    Get Text    css=body
    ${pos_anderson}=    Evaluate    $page_text.find('Anderson2021')
    ${pos_smith}=    Evaluate    $page_text.find('Smith2020')
    Should Be True    ${pos_anderson} < ${pos_smith}

User Can Combine Type Filter And Sorting
    [Documentation]    User can filter by type and sort results
    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id=search-button    timeout=10s
    Click Button    id=search-button
    Wait Until Page Contains Element    id=filter-type    timeout=10s
    Select From List By Label    id=filter-type    Article
    Select From List By Value    id=sort-by    oldest
    Click Button    id=search-button
    Wait Until Page Contains    Smith, John    timeout=10s
    Page Should Contain    Brown, Alice
    Page Should Not Contain    Anderson, James
    ${page_text}=    Get Text    css=body
    ${pos_smith}=    Evaluate    $page_text.find('Smith2020')
    ${pos_brown}=    Evaluate    $page_text.find('Brown2022')
    Should Be True    ${pos_smith} < ${pos_brown}

User Can Combine Tag Filter And Sorting
    [Documentation]    User can filter by tag and sort results
    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id=search-button    timeout=10s
    Click Button    id=search-button
    Wait Until Page Contains Element    id=tag-filter    timeout=10s
    Select From List By Label    id=tag-filter    machine-learning
    Select From List By Value    id=sort-by    title
    Click Button    id=search-button
    Wait Until Page Contains    Smith, John    timeout=10s
    Page Should Contain    Brown, Alice
    ${page_text}=    Get Text    css=body
    ${pos_advanced}=    Evaluate    $page_text.find('Advanced')
    ${pos_cloud}=    Evaluate    $page_text.find('Cloud')
    Should Be True    ${pos_advanced} < ${pos_cloud}

User Can Combine Search Query With Filter And Sort
    [Documentation]    User can search, filter and sort together
    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id=search-query    timeout=10s
    Input Text    id=search-query    Machine
    Click Button    id=search-button
    Wait Until Page Contains Element    id=filter-type    timeout=10s
    Select From List By Label    id=filter-type    Article
    Select From List By Value    id=sort-by    oldest
    Click Button    id=search-button
    Wait Until Page Contains    Smith, John    timeout=10s
    Page Should Not Contain    Anderson, James
    Page Should Not Contain    Johnson, Mary

User Can Filter With Type And Tag Together
    [Documentation]    User can apply both type and tag filters simultaneously
    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id=search-button    timeout=10s
    Click Button    id=search-button
    Wait Until Page Contains Element    id=filter-type    timeout=10s
    Select From List By Label    id=filter-type    Article
    Select From List By Label    id=tag-filter    machine-learning
    Click Button    id=search-button
    Wait Until Page Contains    Smith, John    timeout=10s
    Page Should Contain    Brown, Alice
    Page Should Not Contain    Anderson, James
    Page Should Not Contain    Johnson, Mary

All Three Filters Can Be Combined
    [Documentation]    Search query, type filter and tag filter work together
    Go To    ${BASE_URL}/search
    Wait Until Element Is Visible    id=search-query    timeout=10s
    Input Text    id=search-query    Learning
    Click Button    id=search-button
    Wait Until Page Contains Element    id=filter-type    timeout=10s
    Select From List By Label    id=filter-type    Article
    Select From List By Label    id=tag-filter    machine-learning
    Select From List By Value    id=sort-by    title
    Click Button    id=search-button
    Wait Until Page Contains    Smith, John    timeout=10s
    Page Should Not Contain    Anderson, James
    Page Should Not Contain    Johnson, Mary