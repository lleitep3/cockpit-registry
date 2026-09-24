# Frontend estático AWS com baixo custo

## Padrão

Para um frontend estático, usar S3 privado como origin, CloudFront como entrada
pública e Origin Access Control para permitir leitura somente pela distribuição.

Sem domínio próprio, o MVP pode usar o hostname padrão `*.cloudfront.net` com
HTTPS gerenciado pelo CloudFront. Ao adicionar domínio, solicitar certificado
público ACM em `us-east-1`, requisito do CloudFront.

## Região

O bucket pode ficar na região do cliente, por exemplo `sa-east-1`. CloudFront é
global e entrega por edge locations. A transferência do origin AWS para CloudFront
deve ser considerada nas estimativas, assim como requests, invalidações e storage.

## Gaps a confirmar

- domínio e DNS;
- fallback de SPA;
- estratégia de versionamento e rollback;
- pipeline OIDC;
- budgets e alertas;
- headers de segurança e política de cache.
