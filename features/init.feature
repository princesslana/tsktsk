Feature: Initialize

  Scenario: when initializing tsktsk
    When I run tsktsk init
    Then its exit code should be 0
    And its stderr should be
      """
      Tsktsk initialized.

      """
     And the file .tsktsk should exist

  Scenario: when tsktsk already initialized
    Given I have run tsktsk init
    When I run tsktsk init
    Then its exit code should be 1
    And its stderr should be
      """
      Tsktsk already initialized.

      """
