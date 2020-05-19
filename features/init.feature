Feature: Initialize

  Scenario: when initializing tsktsk
    When I run tsktsk init
    Then its exit code should be 0
     And its output should be
         """
         Initialized tsktsk.

         """
     And the file .tsktsk should exist
