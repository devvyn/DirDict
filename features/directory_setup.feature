Feature: Setup storage directory, clean up on destruction

  Scenario: First time initialization of storage directory for saved files
    Given the storage directory does not exist
    When the storage directory is initialized
    Then the storage directory exists

  Scenario: Attempting to initialize when already initialized
    Given the storage directory exists
    When the storage directory is initialized
    Then the storage directory exists

  Scenario: Destroying the storage directory
    Given the storage directory exists
    When the storage directory is ordered to self-destruct
    Then the storage directory does not exist
