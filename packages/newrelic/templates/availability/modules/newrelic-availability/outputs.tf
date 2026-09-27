output "monitor_guids" { value = { for key, monitor in newrelic_synthetics_monitor.endpoint : key => monitor.id } }
output "dashboard_permalink" { value = newrelic_one_dashboard.availability.permalink }
output "policy_id" { value = newrelic_alert_policy.availability.id }
