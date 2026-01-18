Feature: Save and load

  Background: Fresh keys only, I insist!
    Given I don't accept keys more than 60 minutes old
    And my example text is "Spam & eggs with toast and Spam"
    And the container is initialized

  Scenario: Request expired key
    Given a file that's 61 minutes old
    When I request that key
    Then a 'KeyError' exception is raised
    And that storage key is not in the collection of stored keys
    And the storage directory contains no file that matches the key by name

