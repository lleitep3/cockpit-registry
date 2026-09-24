# Revisão de infraestrutura como código

## Objetivo

Revisar mudanças de Terraform/IaC como um sistema integrado antes do merge ou
apply, identificando riscos técnicos, operacionais, de segurança e custo.

## Perguntas centrais

- Os componentes alterados têm dependências, consumidores e ordem de criação claras?
- Variáveis têm tipos, validações, defaults seguros e flexibilidade por ambiente?
- Outputs expõem exatamente o contrato necessário, sem vazar secrets?
- Região, conta, state, providers e aliases estão coerentes?
- O CI valida o mesmo caminho que será aplicado?
- Existe rollback realista para mudanças destrutivas ou irreversíveis?
- Custos, alertas, tags, logs, backup e ownership estão definidos?

## Resultado esperado

Findings devem citar localização, evidência, impacto e correção. Separar blockers
de melhorias e registrar decisões ainda abertas em vez de inventar valores.
