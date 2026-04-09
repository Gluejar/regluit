Feature: Authentication
  As a user of unglue.it
  I want to register, login, and manage my password
  So that I can participate in the platform

  Scenario: Login page loads with form
    Given I visit "/accounts/login/"
    Then the response status is 200
    And the page contains "csrfmiddlewaretoken"
    And the page contains "username"
    And the page contains "password"

  Scenario: Registration page loads with form
    Given I visit "/accounts/register/"
    Then the response status is 200
    And the page contains "csrfmiddlewaretoken"
    And the page contains "username"
    And the page contains "email"

  Scenario: Password reset page loads
    Given I visit "/accounts/password_reset/"
    Then the response status is 200
    And the page contains "email"

  Scenario: Login page includes Turnstile CAPTCHA
    Given I visit "/accounts/login/"
    Then the response status is 200
    And the page contains "turnstile"
