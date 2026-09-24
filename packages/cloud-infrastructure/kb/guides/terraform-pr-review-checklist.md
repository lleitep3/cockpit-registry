# Checklist de PR Terraform

## Estrutura

- [ ] Root module está no ambiente correto.
- [ ] Módulos reutilizáveis seguem o padrão existente.
- [ ] Providers e versões estão fixados ou controlados.
- [ ] State é separado por ambiente e protegido.

## Contratos

- [ ] Variáveis têm tipos explícitos, validações e descrição.
- [ ] Defaults não habilitam acesso público ou custos inesperados.
- [ ] Secrets são sensíveis e vêm de mecanismo externo.
- [ ] Outputs são úteis para consumidores e não expõem dados desnecessários.

## Segurança e operação

- [ ] Least privilege e OIDC são usados quando aplicável.
- [ ] Criptografia, acesso público, logs e retenção foram avaliados.
- [ ] Plan foi revisado e não contém destruições inesperadas.
- [ ] Smoke tests, observabilidade e rollback estão documentados.

## Validação

- [ ] `terraform fmt -check -recursive`.
- [ ] `terraform init -backend=false`.
- [ ] `terraform validate`.
- [ ] lint, scan e policy checks aplicáveis.
- [ ] CI cobre os ambientes e caminhos alterados.
