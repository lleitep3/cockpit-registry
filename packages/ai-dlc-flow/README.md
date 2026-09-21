# ai-dlc-flow

V0 conceitual e estrutural para conduzir projetos de software desde a intenção até a operação, mantendo decisões humanas, trabalho executável e evidências rastreáveis.

## Escopo do V0

O pacote formaliza:

- lifecycle adaptativo e transições;
- tipos de artefato e cadeia de rastreabilidade;
- work units, dependências, blockers e readiness;
- evidência e gates sem promoção implícita;
- distinção entre decisões humanas e verificações automatizáveis;
- métricas de fluxo e forecast com confiança explícita;
- princípios para autonomia de agentes;
- fronteiras propostas para skills, agentes e workflows futuros.

O pacote também disponibiliza um control panel local, independente do provider, para
acompanhar intenções paralelas, decisões, escopo e lifecycle diretamente a partir do
repositório de documentação.

O V0 não contém controlador executável, agente autônomo, integração com GitHub ou automação de merge. Esses itens dependem de dados observados e pertencem às evoluções V1–V3.

## Modelo curto

```text
Project → Intention(s) → Artifact → Work Unit → Evidence → Gate → Metric → Forecast
```

O projeto pode carregar várias intenções em paralelo. Cada intenção possui seu próprio lifecycle, gates, dependências e blockers. O lifecycle macro não bloqueia ciclos menores, e uma intenção bloqueada não congela as demais, salvo quando o blocker tiver escopo `shared` ou `project`.

O painel deve distinguir três níveis:

1. **Portfólio:** quais intenções estão ativas, bloqueadas, aguardando decisão ou concluídas.
2. **Foco operacional:** qual intenção merece atenção agora e por quê.
3. **Detalhe:** artefatos, work units, evidências, gates e próximo movimento da intenção selecionada.

## Princípios não negociáveis

1. `Specification != Prototype != POC != Implementation != Production Evidence`.
2. Um artefato só muda de classe quando a evidência correspondente existe e está registrada.
3. `Commits != Progress`; progresso é derivado de work units, gates e evidências.
4. Agente propõe, executa e verifica dentro da autorização recebida; humano decide intenção, escopo, risco, política clínica/privacidade e aceitação.
5. Forecast sem histórico deve exibir intervalo amplo, baixa confiança e dados faltantes.

## Conteúdo

- [Modelo central](kb/concepts/core-model.md)
- [Evidência e gates](kb/concepts/evidence-and-gates.md)
- [Métricas e forecast](kb/concepts/metrics-and-forecast.md)
- [Autonomia e oportunidades](kb/concepts/autonomy-and-opportunities.md)
- [Modelo formal em YAML](models/state-model.yaml)
- [Skill roteadora](skills/ai-dlc-flow/SKILL.md)
- [Contrato de intenções do painel](control-panel/project-contract.example.json)

## Control panel local

Depois de instalar o pacote, conecte o repositório de docs e inicie o serviço:

```bash
cockpit ai-dlc-flow control-panel configure \
  ~/projects/partilhar-aba/partilhar-aba-docs
cockpit ai-dlc-flow control-panel start
```

O endereço padrão é `http://127.0.0.1:8765/partilhar/`. O serviço aceita um host e
uma porta diferentes, mas não exige banco, Node, Svelte ou uma API de IA. Ele apenas
lê o repositório configurado e expõe um contrato JSON em `/partilhar/api/project`.

O contrato opcional `ai-dlc-flow.json` ou `.ai-dlc-flow/project.json` permite registrar
o nome, a data de início, a fase atual, o foco e as intenções paralelas. Na ausência
dele, o painel faz uma leitura conservadora dos documentos existentes e marca o que
não estiver registrado como desconhecido.

O painel possui três níveis de leitura:

1. **Portfólio:** intenções ativas, bloqueadas, aguardando ou concluídas.
2. **Foco:** a intenção escolhida para o próximo movimento operacional.
3. **Detalhe:** lifecycle, decisões e escopo atual da intenção selecionada.

### Fontes e compatibilidade

O painel respeita títulos, objetivos e próximas ações do contrato, sem substituir
seu significado por rótulos associados a IDs de outro projeto. IDs estáveis não
determinam o escopo. O documento vigente vem de `scope.source` ou
`analysis.current_scope_artifact` em `dashboard/data.json`. Uma fonte explícita
inválida gera estado vazio, sem retornar silenciosamente a um escopo antigo.

O contrato expõe `scope`; `scope_b` e a rota `scope-b` continuam como aliases para
links antigos, com o mesmo conteúdo vigente. A navegação nova usa `scope`.
Nenhuma dessas adaptações promove gates ou altera decisões do projeto.

Verificação: `python -m unittest discover -s packages/ai-dlc-flow/control-panel/tests`.

Dentro do detalhe de cada intenção, a navegação separa explicitamente **o que já
passou**, **o que está em construção** e **o próximo movimento**. A troca entre
intenções não altera o estado de nenhuma delas; ela apenas muda o foco visual.

Para parar ou consultar o serviço:

```bash
cockpit ai-dlc-flow control-panel status
cockpit ai-dlc-flow control-panel stop
```

## Roadmap

- **V0 — Knowledge + State Model:** este pacote.
- **V1 — Project Control:** inspect-project, readiness, blockers, plan, forecast e replan, com eventos observáveis.
- **V2 — Inception Automation:** descoberta, produto, arquitetura, UX e QA com gates humanos.
- **V3 — Construction Automation:** work unit → implementação → testes → review → evidence → merge → atualização do plano.


## Boilerplate de CI documental

Projetos novos que usem AI-DLC devem copiar
`boilerplates/docs-project/` para a raiz do repositório. O boilerplate inclui:

- `.github/workflows/validate-ai-dlc-docs.yml`;
- `scripts/validate_ai_dlc_docs.py`;
- `scripts/test_validate_ai_dlc_docs.py`.

O CI verifica o núcleo documental e exige título e `Status` explícito nos
documentos alterados. Ele valida contrato documental; não conta commits como
progresso de produto.
