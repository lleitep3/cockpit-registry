module "cognito" {
  source = "../../modules/cognito"

  project_name         = var.project_name
  environment          = var.environment
  domain_prefix        = var.domain_prefix
  enable_google        = var.enable_google
  google_client_id     = var.google_client_id
  google_client_secret = var.google_client_secret
  clients              = var.clients
}

