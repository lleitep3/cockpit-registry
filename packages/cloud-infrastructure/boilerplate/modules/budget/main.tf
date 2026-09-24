locals {
  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      CostCenter  = var.cost_center
      ManagedBy   = "terraform"
      Component   = "governance"
    },
    var.tags,
  )
}

resource "aws_budgets_budget" "monthly" {
  name         = "${var.project_name}-${var.environment}-monthly"
  budget_type  = "COST"
  limit_amount = tostring(var.monthly_budget_usd)
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_filter {
    name   = "TagKeyValue"
    values = [format("CostCenter$%s", var.cost_center)]
  }

  dynamic "notification" {
    for_each = var.budget_alert_email == "" ? [] : [50, 80, 100]

    content {
      comparison_operator        = "GREATER_THAN"
      threshold                  = notification.value
      threshold_type             = "PERCENTAGE"
      notification_type          = "FORECASTED"
      subscriber_email_addresses = [var.budget_alert_email]
    }
  }

  tags = local.common_tags
}
