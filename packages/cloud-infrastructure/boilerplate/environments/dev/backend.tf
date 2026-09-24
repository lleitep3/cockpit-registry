terraform {
  backend "s3" {
    key          = "__PROJECT_NAME__/dev/__AWS_REGION__/identity.tfstate"
    use_lockfile = true
  }
}

