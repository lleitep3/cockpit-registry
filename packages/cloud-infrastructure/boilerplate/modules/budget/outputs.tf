output "budget_name" {
  description = "Created AWS budget name."
  value       = aws_budgets_budget.monthly.name
}

output "budget_arn" {
  description = "Created AWS budget ARN."
  value       = aws_budgets_budget.monthly.arn
}
