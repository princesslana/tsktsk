Feature: Value

  Scenario: when setting task value high
    Given I have run tsktsk init
     When I run tsktsk new --value=high First Task
     Then its exit code should be 0
      And its stdout should be
        """
             1 📦 NEW: First Task                                         V⬆

        """

  Scenario: when setting task value low
    Given I have run tsktsk init
     When I run tsktsk new --value=low First Task
     Then its exit code should be 0
      And its stdout should be
        """
             1 📦 NEW: First Task                                         V⬇

        """
