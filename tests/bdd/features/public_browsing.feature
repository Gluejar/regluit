Feature: Public browsing
  As a visitor to unglue.it
  I want to browse free ebooks and search the catalog
  So that I can discover and download free ebooks

  Scenario: Homepage loads
    Given I visit "/"
    Then the response status is 200
    And the page contains "Unglue.it"

  Scenario: Free ebooks page loads
    Given I visit "/free/"
    Then the response status is 200
    And the page contains "free"

  Scenario Outline: Free ebooks sort options work
    Given I visit "/free/?order_by=<sort>"
    Then the response status is 200

    Examples:
      | sort    |
      | popular |
      | newest  |
      | title   |

  Scenario: Free ebooks pagination works
    Given I visit "/free/?page=2"
    Then the response status is 200

  Scenario: Work detail page loads
    Given I visit "/work/15/"
    Then the response status is 200

  Scenario: Work editions page loads
    Given I visit "/work/15/editions/"
    Then the response status is 200

  Scenario: Search page loads
    Given I visit "/search/?q=moby+dick"
    Then the response status is 200
    And the page contains "search"

  Scenario: Creative Commons page loads
    Given I visit "/creativecommons/"
    Then the response status is 200

  Scenario: Creative Commons by-license page loads
    Given I visit "/creativecommons/by/"
    Then the response status is 200

  Scenario: About page loads
    Given I visit "/info/about.html"
    Then the response status is 200

  Scenario: Terms page loads
    Given I visit "/info/terms.html"
    Then the response status is 200

  Scenario: MARC records page loads
    Given I visit "/marc/"
    Then the response status is 200

  Scenario: Nonexistent page returns 404
    Given I visit "/nonexistent-page-xyz/"
    Then the response status is 404
