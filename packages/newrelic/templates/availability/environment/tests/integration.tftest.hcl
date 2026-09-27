mock_provider "newrelic" {}
variables {
  newrelic_account_id = 12345
  newrelic_region     = "US"
  newrelic_api_key    = "offline-mock-placeholder"
  project_name        = "partilhar"
  environment         = "dev"
  client              = "clinic"
  cost_center         = "pilot"
  endpoints           = { api = "https://api.example.com/health", web = "https://example.com" }
  notification_email  = "operator@example.com"
  free_plan_confirmed = true
}
run "environment_wiring" {
  command = plan
  assert {
    condition     = toset(keys(output.monitor_guids)) == toset(["api", "web"])
    error_message = "The environment must wire both public endpoints into availability monitoring."
  }
}
run "reject_aws_region" {
  command = plan
  variables { newrelic_region = "sa-east-1" }
  expect_failures = [var.newrelic_region]
}
