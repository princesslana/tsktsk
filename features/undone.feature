Feature: Done

  Scenario: when marking a task as udone
    Given I have run tsktsk init
      And I have run tsktsk new First Task
      And I have run tsktsk done 1
     When I run tsktsk undone 1
     Then its exit code should be 0
     When I run tsktsk list
     Then its stdout should be
        """
             1 📦 NEW: First Task

        """
