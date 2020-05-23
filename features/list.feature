Feature: List

  Scenario: sorts by key by default
    Given I have run tsktsk init
      And I have run tsktsk new First Task
      And I have run tsktsk new Second Task
     When I run tsktsk list
     Then its exit code should be 0
      And its stdout should be
        """
             1 📦 NEW: First Task
             2 📦 NEW: Second Task

        """

  Scenario: sorts by roi
    Given I have run tsktsk init
      And I have run tsktsk new --value=high First Task
      And I have run tsktsk new --effort=low Second Task
      And I have run tsktsk new --effort=low --value=high Third Task
     When I run tsktsk list
     Then its exit code should be 0
      And its stdout should be
        """
             3 📦 NEW: Third Task                                         V⬆ E⬇
             2 📦 NEW: Second Task                                           E⬇
             1 📦 NEW: First Task                                         V⬆

        """

