variable "project_name" {
  description = "Stable project identifier used in resource names and tags."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "project_name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "environment" {
  description = "Deployment environment."
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be dev, staging, or prod."
  }
}

variable "user_pool_name" {
  description = "Optional explicit Cognito User Pool name."
  type        = string
  default     = null
}

variable "domain_prefix" {
  description = "Unique Cognito domain prefix for the AWS account and region."
  type        = string
  default     = null

  validation {
    condition     = var.domain_prefix == null || can(regex("^[a-z0-9-]+$", var.domain_prefix))
    error_message = "domain_prefix must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "email_sending_account" {
  description = "Cognito email delivery mode. DEVELOPER requires an SES configuration."
  type        = string
  default     = "COGNITO_DEFAULT"

  validation {
    condition     = contains(["COGNITO_DEFAULT", "DEVELOPER"], var.email_sending_account)
    error_message = "email_sending_account must be COGNITO_DEFAULT or DEVELOPER."
  }
}

variable "enable_google" {
  description = "Whether to configure Google federation and Cognito OAuth endpoints."
  type        = bool
  default     = false
}

variable "google_client_id" {
  description = "Google OAuth client ID. Required when enable_google is true."
  type        = string
  default     = null
}

variable "google_client_secret" {
  description = "Google OAuth client secret. Required when enable_google is true."
  type        = string
  default     = null
  sensitive   = true
}

variable "google_authorize_scopes" {
  description = "Scopes requested from Google during federated sign-in."
  type        = string
  default     = "openid email profile"
}

variable "clients" {
  description = "Public Cognito app clients and their OAuth callback/logout URLs."
  type = map(object({
    callback_urls = list(string)
    logout_urls   = list(string)
  }))

  validation {
    condition     = length(var.clients) > 0
    error_message = "At least one public app client must be configured."
  }
}

variable "tags" {
  description = "Additional tags applied to Cognito resources."
  type        = map(string)
  default     = {}
}

