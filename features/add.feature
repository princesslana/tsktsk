Feature: Add

  Scenario: when adding a new task
    Given I have run tsktsk init
     When I run tsktsk new Setup Project
     Then its exit code should be 0
      And its stdout should be
        """
             1 📦 NEW: Setup Project

        """
     When I run tsktsk list
     Then its exit code should be 0
      And its stdout should be
        """
             1 📦 NEW: Setup Project

        """


  Scenario: when adding two tasks
    Given I have run tsktsk init
     When I run tsktsk new First Task
     Then its exit code should be 0
      And its stdout should be
        """
             1 📦 NEW: First Task

        """
     When I run tsktsk new Second Task
     Then its exit code should be 0
      And its stdout should be
        """
             2 📦 NEW: Second Task

        """
     When I run tsktsk list
     Then its exit code should be 0
      And its stdout should be
        """
             1 📦 NEW: First Task
             2 📦 NEW: Second Task

        """

  Scenario: when adding all categories
    Given I have run tsktsk init
      And I have run tsktsk new Something new
      And I have run tsktsk imp Something improved
      And I have run tsktsk fix Something fixed
      And I have run tsktsk doc Something documented
      And I have run tsktsk tst Something tested
     When I run tsktsk list
     Then its stdout should be
        """
             1 📦 NEW: Something new
             2 👌 IMP: Something improved
             3 🐛 FIX: Something fixed
             4 📖 DOC: Something documented
             5 ✅ TST: Something tested

        """
