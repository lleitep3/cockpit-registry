mock_provider "newrelic" {}
variables {
  free_plan_confirmed = true
  account_id          = 12345
  name_prefix         = "partilhar-dev"
  endpoints           = { api = "https://api.example.com/health", web = "https://example.com" }
  notification_email  = "operator@example.com"
  tags                = { Project = "partilhar", Environment = "dev", Client = "clinic", CostCenter = "pilot", ManagedBy = "terraform" }
}
run "private_free_availability" {
  command = plan
  assert {
    condition     = length(newrelic_synthetics_monitor.endpoint) == 2 && alltrue([for m in newrelic_synthetics_monitor.endpoint : m.type == "SIMPLE" && m.verify_ssl && m.period == "EVERY_5_MINUTES" && length(m.locations_public) == 1 && contains(m.locations_public, "AWS_SA_EAST_1") && length(m.custom_header) == 0])
    error_message = "Only two HTTPS ping monitors at one location, with no credentials, are allowed."
  }
  assert {
    condition     = newrelic_one_dashboard.availability.permissions == "private" && alltrue([for c in newrelic_nrql_alert_condition.availability : c.open_violation_on_expiration && c.expiration_duration == 1200])
    error_message = "Dashboard must stay private and silent monitors must alert."
  }
  assert {
    condition     = one(one(newrelic_workflow.availability.issues_filter).predicate).attribute == "labels.policyIds" && one(one(newrelic_workflow.availability.issues_filter).predicate).operator == "EXACTLY_MATCHES"
    error_message = "Workflow must not collect unrelated account issues."
  }
}
run "rollback_disables_collection" {
  command = plan
  variables { enabled = false }
  assert {
    condition     = !newrelic_workflow.availability.enabled && alltrue([for m in newrelic_synthetics_monitor.endpoint : m.status == "DISABLED"]) && alltrue([for c in newrelic_nrql_alert_condition.availability : !c.enabled])
    error_message = "Rollback must disable monitors and alert delivery without deletion."
  }
}
run "reject_secret_in_url" {
  command = plan
  variables { endpoints = { api = "https://api.example.com/health?token=example", web = "https://example.com" } }
  expect_failures = [var.endpoints]
}
run "reject_invalid_account" {
  command = plan
  variables { account_id = 0 }
  expect_failures = [var.account_id]
}

run "reject_unconfirmed_plan" {
  command = plan
  variables { free_plan_confirmed = false }
  expect_failures = [newrelic_synthetics_monitor.endpoint]
}
