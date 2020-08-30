Feature: Task Dependency

  Scenario: when adding a task with nonexistent dependencies
    Given I have run tsktsk init
     When I run tsktsk new --dep=2 First Task
     Then its exit code should be 1
      And its stderr should be
        """
        Nonexistent task(s): 2

        """

  Scenario: when adding and removing the same dependency
    Given I have run tsktsk init
     When I run tsktsk new First Task
     When I run tsktsk new Second Task
     When I run tsktsk edit 2 --dep 1 --rm-dep 1
     Then its exit code should be 1
      And its stderr should be
        """
        Dependency cannot be added and removed simultaneously

        """

  Scenario: when editing task by adding itself as a dependency
    Given I have run tsktsk init
     When I run tsktsk new First Task
     When I run tsktsk edit 1 --dep 1
     Then its exit code should be 1
      And its stderr should be
        """
        Task cannot be dependent on itself

        """

  Scenario: when adding or removing nonexistent tasks as dependencies
    Given I have run tsktsk init
     When I run tsktsk new First Task
     When I run tsktsk edit 1 --dep 2
     Then its exit code should be 1
      And its stderr should be
        """
        Nonexistent task(s): 2

        """
     When I run tsktsk edit 1 --rm-dep 2
     Then its exit code should be 1
      And its stderr should be
        """
        Nonexistent task(s): 2

        """

  Scenario: removing dependency between independent tasks
    Given I have run tsktsk init
     When I run tsktsk new First Task
     When I run tsktsk new Second Task
     When I run tsktsk edit 1 --rm-dep 2
     Then its exit code should be 0
      And its stdout should be
        """
             1 📦 NEW: First Task

        """
