module "availability" {
  source              = "../modules/newrelic-availability"
  account_id          = var.newrelic_account_id
  name_prefix         = "${var.project_name}-${var.environment}"
  endpoints           = var.endpoints
  notification_email  = var.notification_email
  location            = var.location
  enabled             = var.enabled
  free_plan_confirmed = var.free_plan_confirmed
  tags = {
    Client      = var.client
    Project     = var.project_name
    Environment = var.environment
    CostCenter  = var.cost_center
    ManagedBy   = "terraform"
  }
}
