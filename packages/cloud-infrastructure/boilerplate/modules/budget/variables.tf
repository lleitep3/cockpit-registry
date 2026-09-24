variable "project_name" {
  description = "Stable project identifier used in the budget name and tags."
  type        = string
}

variable "environment" {
  description = "Environment represented by this budget."
  type        = string
}

variable "cost_center" {
  description = "Cost allocation tag value used to filter the budget."
  type        = string
}

variable "monthly_budget_usd" {
  description = "Monthly budget limit in USD."
  type        = number

  validation {
    condition     = var.monthly_budget_usd > 0
    error_message = "monthly_budget_usd must be greater than zero."
  }
}

variable "budget_alert_email" {
  description = "Email for forecasted budget alerts."
  type        = string
  default     = ""
}

variable "tags" {
  description = "Additional tags applied to the budget."
  type        = map(string)
  default     = {}
}
