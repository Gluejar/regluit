Feature: OPDS feeds
  As a library catalog or ebook reader app
  I want to access OPDS feeds from unglue.it
  So that I can discover and import free ebooks

  Scenario: OPDS catalog root returns valid XML
    Given I visit "/api/opds/"
    Then the response status is 200
    And the content type contains "xml"
    And the page contains "<feed"
    And the page contains "<entry"

  Scenario: OPDS single keyword feed works
    Given I visit "/api/opds/kw.Fiction/"
    Then the response status is 200
    And the content type contains "xml"

  Scenario: OPDS compound keyword returns 404
    Given I visit "/api/opds/kw.Fiction/kw.Science/"
    Then the response status is 404

  Scenario: OPDS acquisition feed returns valid XML
    Given I visit "/api/opds/json/"
    Then the response status is 200
    And the content type contains "xml"
    And the page contains "<feed"

  Scenario: ONIX feed returns XML
    Given I visit "/api/onix/"
    Then the response status is 200
    And the content type contains "xml"

  Scenario: ONIX compound keyword returns 404
    Given I visit "/api/onix/kw.Fiction/kw.Science/"
    Then the response status is 404
