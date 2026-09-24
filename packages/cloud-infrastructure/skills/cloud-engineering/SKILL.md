---
name: cloud-engineering
description: Implementar infraestrutura como código em ciclos pequenos, validados e commitados por componente.
---

# Cloud Engineering

Use esta skill para transformar um plano de arquitetura em infraestrutura
reproduzível.

## Sequência obrigatória

1. Ler o plano e confirmar account ID, região, ambiente e backend do state.
2. Documentar o componente que será criado e a contagem esperada.
3. Criar somente o componente.
4. Formatar, validar, testar e gerar o plano da IaC.
5. Revisar `add`, `change` e `destroy`.
6. Aplicar apenas após aprovação do plano.
7. Verificar o recurso real e seus guardrails.
8. Fazer um commit exclusivo do componente.
9. Criar os códigos consumidores em uma mudança posterior.
10. Fazer outro commit e atualizar a comparação estimado versus realizado.

## Terraform

- Usar providers versionados e lockfile.
- Manter variáveis, locals, outputs e módulos com nomes claros.
- Usar state remoto protegido antes de workloads persistentes ou colaboração.
- Não versionar `terraform.tfvars`, state, planos ou credenciais.
- Usar `plan -out` quando a aplicação precisar ser exatamente a planejada.
- Preferir mudanças pequenas e reversíveis.

## Bloqueios

Pare e peça direção quando a conta, o ambiente, o backend, o custo ou o plano de
rollback não estiverem claros, ou quando o workspace não permitir o commit
exigido pelo processo.
