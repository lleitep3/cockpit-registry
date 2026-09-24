locals {
  name_prefix = "${var.project_name}-${var.environment}"
  pool_name   = coalesce(var.user_pool_name, "${local.name_prefix}-users")
  auth_domain = coalesce(var.domain_prefix, "${local.name_prefix}-auth")
  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
      Component   = "identity"
    },
    var.tags
  )
}

resource "aws_cognito_user_pool" "this" {
  name                     = local.pool_name
  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]
  mfa_configuration        = "OFF"
  deletion_protection      = var.environment == "prod" ? "ACTIVE" : "INACTIVE"

  admin_create_user_config {
    allow_admin_create_user_only = true

    invite_message_template {
      email_subject = "Convite para o __PROJECT_DISPLAY_NAME__"
      email_message = "Você recebeu um convite para acessar o __PROJECT_DISPLAY_NAME__. Usuário: {username}. Senha temporária: {####}. Use esses dados para concluir o primeiro acesso."
      sms_message   = "Convite __PROJECT_DISPLAY_NAME__. Usuário: {username}. Senha temporária: {####}."
    }
  }

  password_policy {
    minimum_length                   = 8
    require_lowercase                = true
    require_numbers                  = true
    require_symbols                  = true
    require_uppercase                = true
    temporary_password_validity_days = 7
  }

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  email_configuration {
    email_sending_account = var.email_sending_account
  }

  schema {
    name                = "email"
    attribute_data_type = "String"
    mutable             = true
    required            = true
  }

  tags = local.common_tags
}

resource "aws_cognito_user_pool_domain" "this" {
  count        = var.enable_google ? 1 : 0
  domain       = local.auth_domain
  user_pool_id = aws_cognito_user_pool.this.id
}

resource "aws_cognito_identity_provider" "google" {
  count = var.enable_google ? 1 : 0

  lifecycle {
    precondition {
      condition = (
        var.google_client_id != null &&
        trimspace(var.google_client_id) != "" &&
        var.google_client_secret != null &&
        trimspace(var.google_client_secret) != ""
      )
      error_message = "google_client_id and google_client_secret are required when enable_google is true."
    }
  }

  user_pool_id  = aws_cognito_user_pool.this.id
  provider_name = "Google"
  provider_type = "Google"

  provider_details = {
    client_id        = var.google_client_id
    client_secret    = var.google_client_secret
    authorize_scopes = var.google_authorize_scopes
  }

  attribute_mapping = {
    email = "email"
  }
}

resource "aws_cognito_user_pool_client" "this" {
  for_each = var.clients

  lifecycle {
    precondition {
      condition     = !var.enable_google || length(each.value.callback_urls) > 0
      error_message = "Each Cognito client needs at least one callback URL when Google is enabled."
    }

    precondition {
      condition     = !var.enable_google || length(each.value.logout_urls) > 0
      error_message = "Each Cognito client needs at least one logout URL when Google is enabled."
    }
  }

  name                                 = "${local.name_prefix}-${each.key}"
  user_pool_id                         = aws_cognito_user_pool.this.id
  generate_secret                      = false
  enable_token_revocation              = true
  prevent_user_existence_errors        = "ENABLED"
  allowed_oauth_flows_user_pool_client = var.enable_google
  allowed_oauth_flows                  = var.enable_google ? ["code"] : []
  allowed_oauth_scopes                 = var.enable_google ? ["openid", "email", "profile"] : []
  supported_identity_providers         = concat(["COGNITO"], var.enable_google ? ["Google"] : [])
  callback_urls                        = var.enable_google ? each.value.callback_urls : []
  logout_urls                          = var.enable_google ? each.value.logout_urls : []
  explicit_auth_flows                  = ["ALLOW_USER_SRP_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"]
  refresh_token_validity               = 30
  access_token_validity                = 1
  id_token_validity                    = 1

  token_validity_units {
    refresh_token = "days"
    access_token  = "hours"
    id_token      = "hours"
  }
}
