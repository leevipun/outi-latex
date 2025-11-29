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
    Sleep    2s
    Input Text       id:author        Smith, John
    Input Text       id:title         Advanced Machine Learning
    Input Text       id:journal       AI Journal
    Input Text       id:year          2020
    Input Text       id:volume        42
    Input Text       id:cite_key      Smith2020
    Input Text       id:new_tag       machine-learning
    Click Button     id:save-reference-button
    Sleep    3s

Add Sample Book Reference
    [Documentation]    Add a sample book reference for testing
    Go To    ${BASE_URL}
    Select From List By Value    id:form    book
    Click Button    id:add_new-button
    Sleep    3s
    Input Text       id:author/editor    Anderson, James
    Input Text       id:title           Data Structures
    Input Text       id:publisher       Tech Press
    Input Text       id:year            2021
    Input Text       id:cite_key        Anderson2021
    Input Text       id:new_tag         algorithms
    Click Button     id:save-reference-button
    Sleep    3s

Add Sample Inproceedings Reference
    [Documentation]    Add a sample Inproceedings reference for testing
    Go To    ${BASE_URL}
    Select From List By Value    id:form    inproceedings
    Click Button    id:add_new-button
    Sleep    3s
    Input Text       id:author        Johnson, Mary
    Input Text       id:title         Big Data Analytics
    Input Text       id:booktitle     Conference Proceedings
    Input Text       id:year          2019
    Input Text       id:cite_key      Johnson2019
    Input Text       id:new_tag       data-science
    Click Button     id:save-reference-button
    Sleep    3s

Add Another Article Reference
    [Documentation]    Add another article reference for testing
    Go To    ${BASE_URL}
    Select From List By Value    id:form    article
    Click Button    id:add_new-button
    Sleep    2s
    Input Text       id:author        Brown, Alice
    Input Text       id:title         Cloud Computing Basics
    Input Text       id:journal       Tech Journal
    Input Text       id:year          2022
    Input Text       id:volume        10
    Input Text       id:cite_key      Brown2022
    Input Text       id:new_tag       machine-learning
    Click Button     id:save-reference-button
    Sleep    3s

*** Test Cases ***
User Can Filter Search Results By Reference Type
    [Documentation]    User can filter search results by reference type
    Go To    ${BASE_URL}/search
    Click Button    id=search-button
    Sleep    2s
    Select From List By Label    id=filter-type    Article
    Click Button    id=search-button
    Sleep    2s
    Page Should Contain    Smith, John
    Page Should Contain    Brown, Alice
    Page Should Not Contain    Anderson, James
    Page Should Not Contain    Johnson, Mary

