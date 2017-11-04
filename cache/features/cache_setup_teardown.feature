Feature: Preparing to save files, cleaning up on destruction

  Scenario: First time initialization of directory for saved files
    Given the directory does not exist
    When the directory is initialized
    Then the directory exists

  Scenario: Attempting to initialize when already initialized
    Given the directory exists
    When the cache is initialized
    Then the directory exists

  Scenario: Destroying cache
    Given the cache is initialized
    When I command the cache to clear
    Then the cache path does not exist
