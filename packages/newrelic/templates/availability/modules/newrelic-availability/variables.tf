variable "account_id" {
  type = number
  validation {
    condition     = var.account_id > 0 && floor(var.account_id) == var.account_id
    error_message = "Provide the verified New Relic account ID (not the AWS account ID)."
  }
}
variable "name_prefix" {
  type = string
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,50}$", var.name_prefix))
    error_message = "Use a short lowercase project/environment prefix."
  }
}
variable "endpoints" {
  type = object({ api = string, web = string })
  validation {
    condition     = alltrue([for url in values(var.endpoints) : can(regex("^https://[A-Za-z0-9.-]+(:[0-9]+)?(/[A-Za-z0-9._~/-]*)?$", url))])
    error_message = "Only HTTPS endpoints without credentials, query strings or fragments are allowed."
  }
}
variable "notification_email" {
  type      = string
  sensitive = true
  validation {
    condition     = can(regex("^[^@ ,]+@[^@ ,]+\\.[^@ ,]+$", var.notification_email))
    error_message = "Provide one verified alert email address."
  }
}
variable "location" {
  description = "One public New Relic location, verified in the destination account."
  type        = string
  default     = "AWS_SA_EAST_1"
}
variable "enabled" {
  type    = bool
  default = true
}
variable "tags" {
  type = map(string)
}

variable "free_plan_confirmed" {
  description = "Set only after verifying the destination account is Free with no paid upgrade."
  type        = bool
  default     = false
}
