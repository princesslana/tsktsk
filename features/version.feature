Feature: Show version

  Scenario: when using --version
    When I run tsktsk --version
    Then its exit code should be 0
     And its stdout should match ^\d+\.\d+\..+$
