output "user_pool_id" {
  description = "Cognito User Pool ID."
  value       = aws_cognito_user_pool.this.id
}

output "user_pool_arn" {
  description = "Cognito User Pool ARN."
  value       = aws_cognito_user_pool.this.arn
}

output "user_pool_endpoint" {
  description = "Cognito User Pool issuer endpoint."
  value       = aws_cognito_user_pool.this.endpoint
}

output "auth_domain" {
  description = "Cognito managed login domain, when Google federation is enabled."
  value       = var.enable_google ? aws_cognito_user_pool_domain.this[0].domain : null
}

output "app_clients" {
  description = "Public app client IDs keyed by configured client name."
  value = {
    for name, client in aws_cognito_user_pool_client.this : name => {
      id = client.id
    }
  }
}

