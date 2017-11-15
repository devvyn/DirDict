Feature: Save and load

  Background: Fresh keys only, I insist!
    Given I don't accept keys more than an hour old

  Scenario: Save a key and value
    Given an empty storage directory
    When I save some text to a key named "whatever"
    Then the storage directory contains a file named "whatever"
    And that file contains the specified text

  Scenario: Request non-existent key
    Given an empty storage directory
    When I request any specific key by name
    Then the absence of the specified key is signalled

  Scenario: Request fresh key
    Given a file that's 1 minute old
    When I request that key
    Then I get the contents of the file that matches the key by name

  Scenario: Request expired key
    Given a file that's 61 minutes old
    When I request that key
    Then the absence of the specified key is signalled
    And that storage key is not in the collection of stored keys
    And the storage directory contains no file that matches the key by name

  Scenario: Delete key
    Given the storage directory contains a file with a given name
    When I delete the storage key that matches the file's name
    Then that storage key is not in the collection of stored keys
    Then the storage directory contains no file that matches the key by name
