Feature: Save text to file, load text from file, reject stale files
  Background:
    Given an expiry time of 60 seconds
    And a newly initialized storage directory
  Scenario: Fresh key requested
    Given the storage directory contains a file that's 6 seconds old
    When I request that file
    Then I receive the contents of that file
  Scenario: Expired key requested
    Given the storage directory contains a file that's 600 seconds old
    When I request that file
    Then a KeyError exception is raised
    And that file no longer exists
  Scenario: Non-existent key requested
    Given a newly initialized storage directory
    When I request any file
    Then a KeyError exception is raised
    And the storage directory is still empty
