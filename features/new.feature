Feature: New

  Scenario: when adding a new task
    Given I have run tsktsk init
     When I run tsktsk new Setup Project
     Then its exit code should be 0
      And its stdout should be
        """
             1 Setup Project

        """
     When I run tsktsk top
     Then its exit code should be 0
      And its stdout should be
        """
             1 Setup Project

        """


  Scenario: when adding two tasks
    Given I have run tsktsk init
     When I run tsktsk new First Task
     Then its exit code should be 0
      And its stdout should be
        """
             1 First Task

        """
     When I run tsktsk new Second Task
     Then its exit code should be 0
      And its stdout should be
        """
             2 Second Task

        """
     When I run tsktsk list
     Then its exit code should be 0
      And its stdout should be
        """
             1 First Task
             2 Second Task

        """
