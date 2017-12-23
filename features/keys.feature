Feature: Key-value storage in a given container

  Background:
    Given my example text is "Spam & eggs with toast and Spam"
    And the container is initialized

  Scenario: Save a key and value
    Given an empty storage directory
    When I save some example text to a key named "whatever.txt"
    Then the storage directory contains a file named "whatever.txt"
    And that file contains the example text

  Scenario: Request non-existent key
    Given an empty storage directory
    When I request any specific key by name
    Then a 'KeyError' exception is raised

  Scenario: Request existing key
    Given a file
    When I request that key
    Then I get the contents of the file that matches the key by name

  Scenario: Delete key
    Given the storage directory contains a file with a given name
    When I delete the storage key that matches the file's name
    Then that storage key is not in the collection of stored keys
    Then the storage directory contains no file that matches the key by name
