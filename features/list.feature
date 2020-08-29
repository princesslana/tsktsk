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

  Scenario: sorts dependents after dependencies
    Given I have run tsktsk init
      And I have run tsktsk new --value=high First Task
      And I have run tsktsk new --effort=low Second Task
      And I have run tsktsk new --effort=low --value=high --dep 2 Third Task
     When I run tsktsk list
     Then its exit code should be 0
      And its stdout should be
        """
             2 📦 NEW: Second Task                                           E⬇
             3 📦 NEW: Third Task                                         V⬆ E⬇
                  🔗 2
             1 📦 NEW: First Task                                         V⬆

        """

  Scenario: sorts dependents by roi
    Given I have run tsktsk init
      And I have run tsktsk new First Task
      And I have run tsktsk new --dep 1 Second Task
      And I have run tsktsk new --effort=low --value=high --dep 1 Third Task
     When I run tsktsk list
     Then its exit code should be 0
      And its stdout should be
        """
             1 📦 NEW: First Task
             3 📦 NEW: Third Task                                         V⬆ E⬇
                  🔗 1
             2 📦 NEW: Second Task
                  🔗 1

        """

  Scenario: sorts tasks by roi taking dependence into account
    Given I have run tsktsk init
      And I have run tsktsk new First Task
      And I have run tsktsk new --value=low --dep 1 Second Task
      And I have run tsktsk new --effort=low --value=high --dep 1 Third Task
      And I have run tsktsk new --effort=low Fourth Task
      And I have run tsktsk new --value=low Fifth Task
      And I have run tsktsk new --dep 4 Sixth Task
      And I have run tsktsk new --dep 5 Seventh Task
     When I run tsktsk list
     Then its exit code should be 0
      And its stdout should be
        """
             4 📦 NEW: Fourth Task                                           E⬇
             1 📦 NEW: First Task
             3 📦 NEW: Third Task                                         V⬆ E⬇
                  🔗 1
             6 📦 NEW: Sixth Task
                  🔗 4
             5 📦 NEW: Fifth Task                                         V⬇
             7 📦 NEW: Seventh Task
                  🔗 5
             2 📦 NEW: Second Task                                        V⬇
                  🔗 1

        """

  Scenario: when tasks list is empty
    Given I have run tsktsk init
     When I run tsktsk list
     Then its exit code should be 0
      And its stderr should be
        """
        No tasks

        """

