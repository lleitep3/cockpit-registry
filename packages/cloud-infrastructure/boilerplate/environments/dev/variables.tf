variable "aws_region" {
  description = "AWS region for the development environment."
  type        = string
  default     = "__AWS_REGION__"
}

variable "project_name" {
  description = "Project identifier used in names and tags."
  type        = string
  default     = "__PROJECT_NAME__"
}

variable "environment" {
  description = "Environment name."
  type        = string
  default     = "dev"
}

variable "domain_prefix" {
  description = "Unique Cognito managed login domain prefix."
  type        = string
}

variable "enable_google" {
  description = "Enable Google federation for this environment."
  type        = bool
  default     = false
}

variable "google_client_id" {
  description = "Google OAuth client ID."
  type        = string
  default     = null
}

variable "google_client_secret" {
  description = "Google OAuth client secret. Prefer TF_VAR_google_client_secret or a CI secret."
  type        = string
  default     = null
  sensitive   = true
}

variable "clients" {
  description = "Public clients and OAuth callback/logout URLs."
  type = map(object({
    callback_urls = list(string)
    logout_urls   = list(string)
  }))
}

