Feature: Effort

  Scenario: when setting task effort high
    Given I have run tsktsk init
     When I run tsktsk new --effort=high First Task
     Then its exit code should be 0
      And its stdout should be
        """
             1 📦 NEW: First Task                                            E⬆

        """

  Scenario: when setting task effort low
    Given I have run tsktsk init
     When I run tsktsk new --effort=low First Task
     Then its exit code should be 0
      And its stdout should be
        """
             1 📦 NEW: First Task                                            E⬇

        """
