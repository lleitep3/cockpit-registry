resource "newrelic_synthetics_monitor" "endpoint" {
  lifecycle {
    precondition {
      condition     = var.free_plan_confirmed
      error_message = "Confirm the destination Free plan before enabling monitoring."
    }
  }
  for_each                  = var.endpoints
  account_id                = var.account_id
  name                      = "${var.name_prefix}-${each.key}"
  type                      = "SIMPLE"
  status                    = var.enabled ? "ENABLED" : "DISABLED"
  period                    = "EVERY_5_MINUTES"
  uri                       = each.value
  locations_public          = [var.location]
  verify_ssl                = true
  bypass_head_request       = true
  treat_redirect_as_failure = true
  dynamic "tag" {
    for_each = var.tags
    content {
      key    = tag.key
      values = [tag.value]
    }
  }
}
resource "newrelic_alert_policy" "availability" {
  account_id          = var.account_id
  name                = "${var.name_prefix}-availability"
  incident_preference = "PER_CONDITION"
}
resource "newrelic_nrql_alert_condition" "availability" {
  for_each                       = newrelic_synthetics_monitor.endpoint
  account_id                     = var.account_id
  policy_id                      = newrelic_alert_policy.availability.id
  name                           = "${var.name_prefix}-${each.key}-availability"
  type                           = "static"
  enabled                        = var.enabled
  description                    = "Repeated HTTP failures or no synthetic signal; does not validate clinical workflows."
  violation_time_limit_seconds   = 86400
  aggregation_window             = 300
  aggregation_method             = "cadence"
  aggregation_delay              = 120
  fill_option                    = "none"
  expiration_duration            = 1200
  open_violation_on_expiration   = true
  close_violations_on_expiration = false
  nrql {
    query = "SELECT filter(count(*), WHERE result = 'FAILED') FROM SyntheticCheck WHERE monitorId = '${each.value.monitor_id}'"
  }
  critical {
    operator              = "above"
    threshold             = 0
    threshold_duration    = 900
    threshold_occurrences = "ALL"
  }
}
resource "newrelic_notification_destination" "email" {
  account_id = var.account_id
  name       = "${var.name_prefix}-email"
  type       = "EMAIL"
  property {
    key   = "email"
    value = var.notification_email
  }
}
resource "newrelic_notification_channel" "email" {
  account_id     = var.account_id
  name           = "${var.name_prefix}-email"
  type           = "EMAIL"
  destination_id = newrelic_notification_destination.email.id
  product        = "IINT"
  property {
    key   = "subject"
    value = "${var.name_prefix}: disponibilidade"
  }
}
resource "newrelic_workflow" "availability" {
  account_id            = var.account_id
  name                  = "${var.name_prefix}-availability"
  enabled               = var.enabled
  enrichments_enabled   = false
  muting_rules_handling = "DONT_NOTIFY_FULLY_OR_PARTIALLY_MUTED_ISSUES"
  issues_filter {
    name = "Only this environment availability policy"
    type = "FILTER"
    predicate {
      attribute = "labels.policyIds"
      operator  = "EXACTLY_MATCHES"
      values    = [newrelic_alert_policy.availability.id]
    }
  }
  destination {
    channel_id            = newrelic_notification_channel.email.id
    notification_triggers = ["ACTIVATED", "CLOSED"]
  }
}
resource "newrelic_one_dashboard" "availability" {
  account_id  = var.account_id
  name        = "${var.name_prefix}-availability"
  permissions = "private"
  page {
    name = "Disponibilidade"
    widget_billboard {
      title  = "Sucesso HTTP (%)"
      row    = 1
      column = 1
      width  = 6
      height = 3
      nrql_query {
        account_id = var.account_id
        query      = "FROM SyntheticCheck SELECT percentage(count(*), WHERE result = 'SUCCESS') WHERE monitorId IN (${join(",", [for m in newrelic_synthetics_monitor.endpoint : "'${m.monitor_id}'"])}) FACET monitorName SINCE 1 hour ago"
      }
    }
    widget_line {
      title  = "Duracao dos checks (ms)"
      row    = 1
      column = 7
      width  = 6
      height = 3
      nrql_query {
        account_id = var.account_id
        query      = "FROM SyntheticCheck SELECT average(duration) WHERE monitorId IN (${join(",", [for m in newrelic_synthetics_monitor.endpoint : "'${m.monitor_id}'"])}) FACET monitorName TIMESERIES SINCE 1 hour ago"
      }
    }
  }
}
