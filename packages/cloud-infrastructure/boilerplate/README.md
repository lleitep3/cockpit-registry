# __PROJECT_DISPLAY_NAME__ — infraestrutura AWS

Infraestrutura declarativa do __PROJECT_DISPLAY_NAME__. Terraform é a fonte de verdade;
aplicações e documentação permanecem em seus próprios repositórios.

## Estado atual

O primeiro root module é environments/dev, com o módulo reutilizável
modules/cognito. Ele cria:

- Cognito User Pool para usuários internos;
- convite administrativo e confirmação por e-mail;
- recuperação por e-mail;
- clientes públicos separados para web e mobile;
- federação Google opcional;
- domínio Cognito necessário para o fluxo OAuth;
- revogação de refresh token;
- proteção contra enumeração de usuários.

O Google fica desligado por padrão no código para permitir validação offline.
Para o ambiente de desenvolvimento, habilite-o somente após configurar as
credenciais OAuth no Google Cloud.

## Conta AWS

Uma conta AWS é necessária para terraform plan contra recursos reais e para
terraform apply. Não é necessária para terraform fmt ou para validar a
configuração sem backend remoto.

Para o primeiro piloto, uma conta AWS única pode hospedar dev. Antes de
staging/prod, separar contas ou ao menos roles e estados por ambiente. Nunca
versionar access keys, secrets, state ou plans.

## Pré-requisitos do primeiro apply

Antes de inicializar o backend remoto, ainda precisamos provisionar:

1. bucket S3 de state com versionamento, criptografia e acesso restrito;
2. role de CI com OIDC do GitHub, sem access key de longa duração;
3. permissões mínimas para a role local/CI;
4. credenciais Google OAuth e URLs de callback aprovadas;
5. região e prefixo Cognito únicos.

O bucket de state é bootstrap: ele precisa existir antes de terraform init com
backend S3. Esse bootstrap deve ter um procedimento próprio e revisão separada.

## Validação local

Na raiz do repositório:

    terraform fmt -check -recursive
    cd environments/dev
    terraform init -backend=false
    terraform validate

Para usar o backend remoto, forneça o bucket fora do código:

    terraform init -backend-config="bucket=<state-bucket>" -backend-config="region=<state-region>"

O arquivo terraform.tfvars é ignorado pelo Git. Copie
environments/dev/terraform.tfvars.example, substitua os valores públicos e
forneça o segredo Google por TF_VAR_google_client_secret.

Não executar apply até que o bucket, a role, as credenciais e o plan tenham
sido revisados. O workflow atual valida o código sem acessar a AWS; plan e
apply federados por OIDC entram em uma etapa posterior.

## Referências

- docs/infra-lifecycle.md
- Terraform S3 backend:
  https://developer.hashicorp.com/terraform/language/backend/s3
- AWS Cognito User Pools:
  https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools.html
