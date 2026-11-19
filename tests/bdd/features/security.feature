Feature: Security headers and behavior
  As a site operator
  I want proper security headers and CSRF protection
  So that users are protected from common web attacks

  Scenario: CSRF cookie is set on login page
    Given I visit "/accounts/login/"
    Then the response status is 200
    And the response has a "csrftoken" cookie

  Scenario: HSTS header is present
    Given I visit "/"
    Then the response status is 200
    And the response header "Strict-Transport-Security" is present

  Scenario: HTTP redirects to HTTPS
    Given I request the HTTP version of "/"
    Then the response redirects to HTTPS
