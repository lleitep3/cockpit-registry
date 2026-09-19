---
name: ai-dlc-flow
description: "Aplica o modelo AI-DLC Flow para registrar estado, evidência, gates, métricas e forecast com autoridade humana explícita."
---

# Skill: ai-dlc-flow

Use esta skill para analisar ou conduzir uma iniciativa seguindo o V0 do AI-DLC Flow.

## Antes de agir

1. Consulte a KB local sobre o projeto e o domínio.
2. Leia as instruções do repositório e as fontes versionadas relevantes.
3. Identifique o lifecycle macro e o ciclo menor da work unit.
4. Inventarie as intenções em paralelo e identifique a intenção em foco.
5. Separe blocker local, blocker compartilhado e blocker de projeto.
6. Separe fato, hipótese, decisão humana, proposta do agente e desconhecido.
7. Inspecione o estado atual antes de editar ou declarar progresso.

## Registro obrigatório

Para cada incremento, registre:

- artefatos lidos e produzidos;
- work unit e estado;
- dependências e blockers, com condição de desbloqueio;
- evidência, nível E0–E5, versão, cenário e limites;
- gate afetado e autoridade necessária;
- métricas observadas ou `unknown`;
- forecast em intervalo, confiança e dados faltantes;
- intenção afetada, escopo do blocker e alternativas desbloqueadas;
- próxima ação ou decisão humana.

## Proteções

- Não trate `Specification`, `Prototype`, `POC`, `Implementation` e `Production Evidence` como equivalentes.
- Não promova classe de evidência implicitamente.
- Não conte commits como progresso entregue.
- Não invente fórmulas clínicas, permissões, datas ou aceites.
- Não registre decisão humana como aprovada porque o usuário não respondeu.
- Não declare produção sem observação no ambiente-alvo.
- Não trate uma intenção bloqueada como bloqueio automático das demais.
- Não escolha o próximo movimento apenas por ordem visual; considere dependências, gates e autoridade necessária.
- Pare diante de blocker, ambiguidade, falta de autorização ou evidência insuficiente.

## Modos conceituais

- `bootstrap`: inventariar fontes, estado e lacunas;
- `readiness`: verificar work units e gates;
- `progress`: calcular estado e métricas observáveis;
- `forecast`: produzir intervalo e confiança explícita;
- `replan`: registrar delta, causa, impacto e próxima ordem.

No V0 esses modos são protocolo de trabalho, não comandos executáveis. Não invente automação onde ainda não existe.


## Bootstrap de projeto documental

Ao iniciar um repositório novo que use AI-DLC para documentação, inclua o
boilerplate versionado em `boilerplates/docs-project/`:

- `.github/workflows/validate-ai-dlc-docs.yml`;
- `scripts/validate_ai_dlc_docs.py`;
- `scripts/test_validate_ai_dlc_docs.py`.

Instale o workflow antes do primeiro PR documental. Ajuste somente os diretórios
necessários e mantenha o validador determinístico. CI valida contratos
documentais; não transforma commits em progresso de produto.
