@fixtures.date
Feature: Velocity

  Scenario: when no past tasks completed to estimate velocity
    Given I have run tsktsk init
      And I have run tsktsk new First Task
     When I run tsktsk list --estimates
     Then its exit code should be 0
      And its stdout should be
        """
             1 📦 NEW: First Task

        """

  Scenario Outline: when velocity is not applicable
    Given today is <past_date>
      And I have run tsktsk init
      And I have run tsktsk new First Task
      And I have run tsktsk new Second Task
      And I have run tsktsk done 1
      And today is <present_date>
     When I run tsktsk list --estimates
     Then its exit code should be 0
      And its stdout should be
        """
             2 📦 NEW: Second Task

        """

  Examples:
      |  past_date | present_date |
      | 2020-07-01 |  2020-09-01  |
      | 2020-09-01 |  2020-09-01  |

  Scenario Outline: velocity from one day
    Given today is <start_date>
      And I have run tsktsk init
      And I have run tsktsk new --effort=<effort> First Task
      And I have run tsktsk new Second Task
      And I have run tsktsk new Third Task
      And I have run tsktsk done 1
    Given today is 2020-09-03
     When I run tsktsk list --estimates
     Then its exit code should be 0
      And its stdout should be
        """
             2 📦 NEW: Second Task                                              ⏰ <task2_eta>
             3 📦 NEW: Third Task                                               ⏰ <task3_eta>

        """

  Examples:
    | start_date | effort | task2_eta | task3_eta |
    | 2020-09-02 | medium |   03-09   |   04-09   |
    | 2020-09-01 | medium |   04-09   |   06-09   |
    | 2020-09-01 |  low   |   06-09   |   09-09   |
    | 2020-09-01 |  high  |   04-09   |   05-09   |
    # 60 days between start_date and current date
    | 2020-07-05 |  high  |   10-10   |   16-11   |

  Scenario Outline: velocity from several days
    Given I have run tsktsk init
      And I have run tsktsk new --effort=<effort1> First Task
      And I have run tsktsk new --effort=<effort2> Second Task
      And I have run tsktsk new --effort=<effort3> Third Task
      And I have run tsktsk new Fourth Task
      And I have run tsktsk new Fifth Task
    Given today is <date1>
      And I have run tsktsk done 1
    Given today is <date2>
      And I have run tsktsk done 2
    Given today is <date3>
      And I have run tsktsk done 3
    Given today is 2020-09-20
     When I run tsktsk list --estimates
     Then its exit code should be 0
      And its stdout should be
        """
             4 📦 NEW: Fourth Task                                              ⏰ <task4_eta>
             5 📦 NEW: Fifth Task                                               ⏰ <task5_eta>

        """

  Examples:
    | effort1 |   date1    | effort2 |   date2     | effort3 |   date3    | task4_eta | task5_eta |
    |  medium | 2020-09-19 |   low   | 2020-09-19  |   low   | 2020-09-19 |   20-09   |   20-09   |
    |   low   | 2020-09-19 |   low   | 2020-09-19  |   low   | 2020-09-19 |   20-09   |   21-09   |
    | medium  | 2020-09-05 | medium  | 2020-09-10  | medium  | 2020-09-15 |   24-09   |   29-09   |
    |   high  | 2020-09-10 |  high   | 2020-09-15  |   high  | 2020-09-20 |   28-09   |   01-10   |
