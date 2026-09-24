# Regra: postura de infraestrutura cloud

Ative esta postura para qualquer tarefa de arquitetura cloud, AWS, Terraform,
infraestrutura como código, billing, segurança de plataforma ou operação de
ambientes.

## Ciclo obrigatório de entrega

Antes de criar um componente:

1. Identifique conta, organização, região, ambiente, proprietário e objetivo.
2. Faça um plano documentado.
3. Estime a quantidade de componentes lógicos necessários.
4. Liste dependências, custo esperado, riscos, critérios de validação e plano de
   rollback.

Para cada componente:

1. Implemente somente o componente planejado.
2. Execute formatadores, validação, testes e plano da ferramenta de IaC.
3. Revise o diff e confirme que não há destruições ou recursos fora do escopo.
4. Faça um commit exclusivo do componente.
5. Só então implemente os códigos consumidores.
6. Faça um segundo commit exclusivo dos consumidores.

Ao finalizar, compare:

| Medida | Planejado | Final | Desvio |
| --- | ---: | ---: | --- |
| Componentes lógicos | preencher | preencher | explicar |
| Recursos IaC | preencher | preencher | explicar |

Se não houver repositório Git, não finja que houve commit. Informe a limitação e
solicite o workspace correto antes de continuar a sequência que exige commits.

## Guardrails

- Não usar conta pessoal como destino permanente de infraestrutura de cliente.
- Confirmar o account ID antes de qualquer `apply`.
- Configurar tags de `Client`, `Project`, `Environment`, `CostCenter` e `ManagedBy`.
- Configurar budget e alertas antes de workloads persistentes.
- Preferir valores pequenos e reversíveis em sandbox.
- Não criar credenciais de longa duração quando uma role ou identidade federada
  for suficiente.
- Não incluir segredos em código, logs, planos versionados, state ou commits.
- Não aplicar destruições, migrações ou mudanças irreversíveis sem confirmação
  explícita e plano revisado.
