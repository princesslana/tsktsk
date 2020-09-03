Feature: Edit

  Scenario: when editing a task
    Given I have run tsktsk init
      And I have run tsktsk new A Task
     When I run tsktsk edit 1 Edited Message
     Then its exit code should be 0
      And its stdout should be
        """
             1 📦 NEW: Edited Message

        """

  Scenario: when editing everything
    Given I have run tsktsk init
      And I have run tsktsk new Dependency 1
      And I have run tsktsk new Dependency 2
      And I have run tsktsk new --dep 1 A Task
     When I run tsktsk edit 1 --category=imp --value=high --effort=low --rm-dep 1 --dep 2 Edited Message
     Then its exit code should be 0
      And its stdout should be
        """
             1 👌 IMP: Edited Message                                     V⬆ E⬇
                  🔗 2

        """


