# AI-DLC Flow — índice da KB

Leia nesta ordem:

1. [`core-model.md`](core-model.md) — conceitos, lifecycle, estado, dependência, readiness e rastreabilidade.
2. [`evidence-and-gates.md`](evidence-and-gates.md) — classificação de artefatos, evidência, gates e autoridade.
3. [`metrics-and-forecast.md`](metrics-and-forecast.md) — métricas de fluxo, estimativa, forecast e confiança.
4. [`autonomy-and-opportunities.md`](autonomy-and-opportunities.md) — limites de autonomia e fronteiras de skills, workflows e agents.

O arquivo [`../../models/state-model.yaml`](../../models/state-model.yaml) é a forma estruturada do contrato. A KB explica o significado; o YAML facilita validação e futura automação.

## Regra de uso

Toda aplicação do modelo deve apontar para a fonte do fato: documento, issue, PR, commit, teste, log sanitizado, observação de runtime ou decisão humana. Conversa sem registro é contexto transitório, não evidência durável.
