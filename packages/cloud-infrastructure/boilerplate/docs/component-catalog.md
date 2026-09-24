# Catálogo de componentes Terraform

O boilerplate inclui componentes reutilizáveis, mas não aplica todos por padrão.
Cada ambiente deve declarar explicitamente quais módulos compõe e documentar o
impacto em custo, segurança e operação.

| Componente | Caminho | Padrões incluídos |
| --- | --- | --- |
| Governance budget | `modules/budget` | CostCenter, limite mensal e alertas previstos |
| Storage private S3 | `modules/private-s3` | bloqueio público, AES-256, versionamento |
| Identity Cognito | `modules/cognito` | pool, clientes públicos, recuperação e Google opcional |
| Environment dev | `environments/dev` | root module, provider e contrato de variáveis |

O catálogo deve crescer somente depois que um componente real for implementado,
validado, documentado e commitado. Componentes experimentais devem permanecer
marcados como opcionais até terem critérios de segurança, custo e rollback.
