Feature: Save text to file, load text from file, reject stale files

  Background:
    Given a path 'spam-eggs.tmp'
    And the time to live is 60 seconds

  Scenario: First time initialization of cache on disk
    Given the cache path does not exist
    When the cache is initialized
    Then the cache path exists
    And the cache path points to a directory
    And cache directory is empty

  Scenario: Re-initializing cache on disk (do nothing)
    When the cache path exists
    And the cache path points to a directory
    When the cache is initialized
    Then the cache path exists
    And the cache path points to a directory

  Scenario: Non-existent key requested
    When the cache is initialized
    And cache directory is empty
    When I request the key 'spam'
    Then a KeyError exception is raised
    And cache directory is empty

  Scenario: Existing, fresh key requested
    Given the cache is initialized
    And the cache path contains file 'spam' with text 'fresh egg', modified 6 seconds ago
    When I request the key 'spam'
    Then I receive the text 'fresh egg'
    
  Scenario: Existing, expired key requested
    Given the cache is initialized
    And the cache path contains file 'spam' with text 'rotten egg', modified 6000 seconds ago
    When I request the key 'spam'
    Then a KeyError exception is raised
    
  Scenario: Destroying cache
    Given the cache in initialized
    When I command the cache to clear
    Then the cache path does not exist
