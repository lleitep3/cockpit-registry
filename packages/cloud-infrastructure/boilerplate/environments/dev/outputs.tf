output "cognito_user_pool_id" {
  description = "Cognito User Pool ID for the development environment."
  value       = module.cognito.user_pool_id
}

output "cognito_user_pool_arn" {
  description = "Cognito User Pool ARN for the development environment."
  value       = module.cognito.user_pool_arn
}

output "cognito_user_pool_endpoint" {
  description = "Cognito User Pool issuer endpoint."
  value       = module.cognito.user_pool_endpoint
}

output "cognito_auth_domain" {
  description = "Cognito managed login domain when Google is enabled."
  value       = module.cognito.auth_domain
}

output "cognito_app_clients" {
  description = "Public Cognito app client IDs."
  value       = module.cognito.app_clients
}

