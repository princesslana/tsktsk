Feature: Done

  Scenario: when marking a task done
    Given I have run tsktsk init
      And I have run tsktsk new First Task
     When I run tsktsk done 1
     Then its exit code should be 0
     When I run tsktsk list
     Then its stdout should be empty
        
