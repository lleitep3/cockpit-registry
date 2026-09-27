variable "newrelic_account_id" { type = number }
variable "newrelic_region" {
  type = string
  validation {
    condition     = contains(["US", "EU"], var.newrelic_region)
    error_message = "Use the verified New Relic data region US or EU, not an AWS region."
  }
}
variable "project_name" { type = string }
variable "environment" { type = string }
variable "client" { type = string }
variable "cost_center" { type = string }
variable "endpoints" { type = object({ api = string, web = string }) }
variable "notification_email" {
  type      = string
  sensitive = true
}
variable "location" {
  type    = string
  default = "AWS_SA_EAST_1"
}
variable "enabled" {
  type    = bool
  default = true
}
variable "free_plan_confirmed" {
  type    = bool
  default = false
}

variable "newrelic_api_key" {
  description = "Supply through TF_VAR_newrelic_api_key from a trusted secret store."
  type        = string
  sensitive   = true
  ephemeral   = true
}
