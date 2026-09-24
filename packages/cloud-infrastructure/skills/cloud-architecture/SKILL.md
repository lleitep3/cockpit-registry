---
name: cloud-architecture
description: Planejar arquiteturas cloud com fronteiras, custos, riscos e contagem explícita de componentes.
---

# Cloud Architecture

Use esta skill antes de criar ou alterar infraestrutura cloud.

## Processo

1. Levante objetivo, dados, usuários, ambientes, disponibilidade, recuperação,
   compliance, equipe, região e orçamento.
2. Confirme a propriedade da conta e quem pagará a fatura.
3. Separe componentes lógicos de recursos concretos do provedor.
4. Crie um plano com uma contagem estimada:

   | Componente | Objetivo | Dependências | Custo estimado | Risco |
   | --- | --- | --- | --- | --- |

5. Registre alternativas rejeitadas e o motivo.
6. Defina ordem de implementação, critérios de aceite e rollback.
7. Depois da implementação, compare estimativa e resultado real.

## Perguntas mínimas

- A conta pertence ao cliente ou ao operador?
- O ambiente é sandbox, desenvolvimento, staging ou produção?
- Quais dados podem existir e qual é a retenção?
- Como os custos serão identificados e alertados?
- Qual é a recuperação aceitável?
- Como a solução será migrada ou encerrada?

Não escolha serviços apenas por familiaridade. Relacione cada serviço a uma
necessidade, ao custo e à capacidade operacional disponível.
