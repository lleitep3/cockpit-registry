terraform {
  required_version = ">= 1.10.0, < 2.0.0"
  required_providers {
    newrelic = { source = "newrelic/newrelic", version = "~> 3.99.3" }
  }
  backend "s3" { use_lockfile = true }
}
# Ephemeral provider input is not persisted in Terraform plans or state.
provider "newrelic" {
  api_key    = var.newrelic_api_key
  account_id = var.newrelic_account_id
  region     = var.newrelic_region
}
