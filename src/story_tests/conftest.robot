*** Settings ***
Documentation     Shared fixtures and setup for Robot Framework tests
Library           RequestsLibrary

*** Keywords ***
Reset Test Database
    [Documentation]    Reset the database to a clean state for testing
    ${response}=    GET    http://localhost:5001/reset_db
    Should Be Equal As Integers    ${response.status_code}    200
    Log    Database reset successfully
