variable "bucket_name" {
  description = "Globally unique private S3 bucket name."
  type        = string
}

variable "project_name" {
  description = "Stable project identifier used in tags."
  type        = string
}

variable "environment" {
  description = "Environment represented by the bucket."
  type        = string
}

variable "cost_center" {
  description = "Cost allocation tag value."
  type        = string
}

variable "versioning_enabled" {
  description = "Whether S3 object versioning is enabled."
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags applied to the bucket."
  type        = map(string)
  default     = {}
}
