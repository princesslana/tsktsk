Feature: Help

  Scenario: when using --help
    When I run tsktsk --help
    Then its exit code should be 0
     And its stdout should be
       """
       Usage: tsktsk [OPTIONS] COMMAND [ARGS]...

       Options:
         --version      Show the version and exit.
         --github TEXT  Manage issues in a github repository.
         --help         Show this message and exit.

       Commands:
         doc   Create a task to improve documentation.
         done  Mark a task as done.
         edit  Edit an existing task.
         fix   Create a task to fix a bug.
         imp   Create a task to improve something existing.
         init  Initialize a new tsktsk repository.
         list  List tasks to be done, with highest value:effort ratio first.
         new   Create a task to add something new.
         tst   Create a task related to testing.

       """

    Scenario: Help for new command
      When I run tsktsk new --help
      Then its exit code should be 0
       And its stdout should be
         """
         Usage: tsktsk new [OPTIONS] MESSAGE...

           Create a task to add something new.

           Uses MESSAGE as a description of this task.

           An estimate of value gained and effort required to complete this task may
           also be added. These estimates are used to order the tasks, such that the
           tasks with the highest value:effort ratio are ordered first. If not
           specified, it defaults to medium/medium.

         Options:
           --value [high|medium|low]   Value gained by completing this task.
           --effort [high|medium|low]  Effort required to complete this task.
           --help                      Show this message and exit.

         """
      
    Scenario: Help for done command
      When I run tsktsk done --help
      Then its exit code should be 0
       And its stdout should be
         """
         Usage: tsktsk done [OPTIONS] KEY

           Mark a task as done. KEY specifies which task.

         Options:
           --help  Show this message and exit.

         """

    Scenario: Help for edit command
      When I run tsktsk edit --help
      Then its exit code should be 0
       And its stdout should be
         """
         Usage: tsktsk edit [OPTIONS] KEY [MESSAGE]...
        
           Edit an existing task. KEY specifies which task.

         Options:
           --category [NEW|IMP|FIX|DOC|TST]
                                           Category of this task.
           --value [high|medium|low]       Value gained by completing this task.
           --effort [high|medium|low]      Effort required to complete this task.
           --help                          Show this message and exit.

          """

    Scenario: Help for init command
      When I run tsktsk init --help
      Then its exit code should be 0
       And its stdout should be
         """
         Usage: tsktsk init [OPTIONS]

           Initialize a new tsktsk repository.

         Options:
           --help  Show this message and exit.

         """

    Scenario: Help for list command
      When I run tsktsk list --help
      Then its exit code should be 0
       And its stdout should be
         """
         Usage: tsktsk list [OPTIONS]

           List tasks to be done, with highest value:effort ratio first.

         Options:
           --help  Show this message and exit.

         """

