Feature: Save text to file, load text from file, reject stale files

  Background: Fresh files only, I insist!
    Given I never want a file that's more than an hour old

  Scenario: Fresh key requested
    Given a stored file that's a minute old
    When I request that file
    Then I receive the contents of that file

  Scenario: Expired key requested
    Given a stored file that's 66 minutes old
    When I request that file
    Then the file is not loaded
    And that file no longer exists

  Scenario: Non-existent key requested
    Given no files
    When I request any file
    Then a KeyError exception is raised
    And the storage directory is still empty
