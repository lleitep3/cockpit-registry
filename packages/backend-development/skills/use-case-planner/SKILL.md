---
name: use-case-planner
description: Conduz sessões de planejamento de fluxos de usuário e casos de uso, produzindo uma ou mais docs versionadas com direcionamentos para produto, app e API antes da implementação. Use quando o primeiro fluxo, caso de uso ou fatia vertical ainda não estiver definido; não use para implementar código sem um fluxo aceito.
---

# Use case planner

Use esta skill para transformar uma intenção de produto em uma fatia vertical
reproduzível. O resultado principal é documentação versionável, não código.

## Quando iniciar a sessão

Inicie uma sessão quando houver pedido para:

- mapear o primeiro fluxo do usuário;
- definir um caso de uso para app, API ou ambos;
- transformar uma ideia em uma fatia vertical executável;
- preparar direcionamentos para produto, design e engenharia;
- revisar se um fluxo já está suficientemente definido para implementação.

Não comece criando endpoint, tela, migration ou entidade. Primeiro leia as
decisões existentes, identifique contradições e produza o pacote documental.

## Fluxo da sessão

1. Inventarie requisitos, decisões, protótipos, APIs e lacunas existentes.
2. Dê ao fluxo um identificador estável, como `FLOW-001`, e ao caso de uso um
   identificador relacionado, como `UC-001`.
3. Descreva o ator, o objetivo e o resultado observável.
4. Mapeie pré-condições, caminho principal e alternativas.
5. Modele estados antes/depois e transições permitidas.
6. Explicite autorização, escopo, vínculos e negações.
7. Liste eventos de auditoria, inclusive consultas sensíveis.
8. Só então proponha o contrato HTTP, se a fatia precisar de API.
9. Escreva cenários permitidos, negados, de borda e de auditoria.
10. Fixe dados fictícios, IDs, relógio, timezone e ordem de execução.
11. Defina critérios de aceite verificáveis.
12. Relacione cada etapa às telas ou estados do app e, quando aplicável, do web.
13. Separe decisões aceitas, propostas e perguntas abertas.

Leia [use-case-planning-workflow.md](references/use-case-planning-workflow.md)
para o formato canônico dos documentos e das evidências.

## Entregáveis

Escolha o menor conjunto que torne a fatia reproduzível:

- documento principal do fluxo e caso de uso;
- diagrama de fluxo ou sequência, quando houver ramificações relevantes;
- plano de testes com cenários Given/When/Then;
- contrato inicial da API, somente quando o caso atravessar o backend;
- matriz de telas e estados do app.

Todos os entregáveis devem referenciar o mesmo `FLOW-*` e `UC-*`. Se uma
decisão ainda estiver aberta, ela não pode aparecer como requisito aceito em
outro documento.

## Gate antes do código

Considere a fatia pronta para implementação somente quando houver:

- ator, objetivo e resultado observável;
- pré-condições e estados sem contradições;
- permissões e negações explícitas;
- auditoria definida;
- dados fictícios reproduzíveis;
- critérios de aceite testáveis;
- telas e contrato alinhados, quando existirem;
- perguntas abertas com responsável e próximo passo.

Depois desse gate, a skill `api-developer` pode transformar o caso de uso em
portas, testes de aplicação, domínio, adaptadores e endpoint.
