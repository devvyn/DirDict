Feature: Storage container setup and teardown

  Background:
    Given the storage directory shall be named "temporary_test_directory"

  Scenario: initialize the container
    When the storage directory is initialized
    Then the storage directory exists

  Scenario: initialize when already initialized
    Given the storage directory already exists
    When the storage directory is initialized
    Then the storage directory exists

  Scenario: Destroying the storage directory
    Given the storage directory already exists
    When the storage directory is ordered to self-destruct
    Then the storage directory does not exist
