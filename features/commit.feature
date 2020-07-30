Feature: Commit

  Scenario: when committing task with no changes
    Given I have a git repository
      And I have run tsktsk init
      And I have run tsktsk new First Task
     When I run tsktsk commit 1
     Then its exit code should be 1
     When I run tsktsk list
     Then its stdout should be
        """
             1 📦 NEW: First Task

        """

  Scenario: when committing task with changes
    Given I have a git repository
      And I have run tsktsk init
      And I have run tsktsk new First Task
      And I have added a file to staging
     When I run tsktsk commit 1
     Then its exit code should be 0
     When I run git log --pretty=%s -1
     Then its stdout should be
        """
        📦 NEW: First Task

        """
     When I run tsktsk list
     Then its stdout should be
        """
             1 📦 NEW: First Task

        """
