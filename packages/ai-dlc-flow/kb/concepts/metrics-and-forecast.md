# Métricas de fluxo, estimativa e forecast

## 1. Fonte da medição

Métricas devem ser calculadas de eventos append-only ou registros versionados. Cada número deve carregar:

- `as_of`;
- fonte e versão do parser;
- população e janela observada;
- completude (`measured`, `partial`, `estimated` ou `unknown`);
- link para a evidência.

Se timestamps ou estados estiverem incompletos, publicar `unknown`/`partial`, não preencher com datas inventadas.

## 2. Métricas V0

| Métrica | Definição | Unidade |
|---|---|---|
| lead time | `ready_at → released_at` | tempo por work unit |
| cycle time | `in_progress_at → verified_at` ou política declarada | tempo por work unit |
| throughput | unidades `accepted`/`released` por janela | unidades/janela |
| blocked time | soma dos intervalos em `blocked` | tempo por unidade/janela |
| rework rate | unidades que entraram em `rework` / unidades encerradas | proporção |
| review time | `in_review_at → review_decision_at` | tempo por unidade |
| scope growth | unidades adicionadas após baseline / baseline comprometida | proporção |
| variance | diferença entre previsão e observado | tempo/unidades |
| WIP | unidades em `in_progress`, `in_review` ou `rework` | contagem |
| state inventory | contagem por estado (`ready`, `building`, `verified`, etc.) | contagem |

Não usar commits, linhas, tokens ou mensagens como substitutos de throughput ou valor.

## 3. Estimativa

Estimativa é uma hipótese antes da execução. Ela deve declarar:

- unidade de medida (work units, horas, pontos ou outra);
- método e referência;
- intervalo, não só um número;
- premissas e exclusões;
- risco e confiança;
- condição que invalida a estimativa.

Sem histórico, usar faixa ampla e ordem de grandeza. Um valor único com aparência de precisão é proibido quando a amostra é insuficiente.

## 4. Forecast

Forecast é atualização probabilística/intervalar baseada no estado atual, histórico e incerteza. No mínimo:

```yaml
scope:
  work_units: [WU-001, WU-002]
  as_of: "timestamp"
interval:
  lower: "valor ou data"
  upper: "valor ou data"
  unit: "work_units|days|weeks"
confidence: low|medium|high
method: "descrição curta"
sample:
  completed_units: 0
  observed_window: "unknown"
assumptions:
  - "premissa"
unknowns:
  - "dado faltante"
risks:
  - "risco"
next_update: "evento que atualiza o forecast"
```

### Confiança

- `low`: sem histórico ou com decisões/gates críticos abertos; intervalo deve ser amplo;
- `medium`: histórico curto, estados e escopo relativamente estáveis;
- `high`: amostra suficiente, definição estável, eventos completos e baixa variância recente.

Confiança é qualidade do forecast, não probabilidade de o produto ser bom.

## 5. Forecast inicial do projeto sem histórico

Quando o projeto ainda está em descoberta/definição:

1. não emitir data de término;
2. forecastar primeiro em quantidade de work units ou marcos;
3. separar trabalho conhecido de decisões pendentes;
4. registrar `confidence: low`;
5. coletar as primeiras 3–5 unidades encerradas com timestamps;
6. recalibrar depois de cada unidade ou mudança de escopo relevante.

Um intervalo de unidades é válido mesmo quando o intervalo de calendário é `unknown`. Isso é mais honesto que converter uma hipótese em prazo.

## 6. Replanejamento

Replan acontece quando:

- gate falha ou uma decisão humana muda;
- blocker excede a política do projeto;
- escopo cresce ou uma dependência muda;
- evidência contradiz requisito/design;
- observação pós-release cria aprendizado relevante.

O replanejamento deve preservar o baseline anterior, registrar delta, causa, impacto em dependências e novo forecast. Não apagar o histórico para fazer a variância desaparecer.
