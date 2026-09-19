# Modelo central do AI-DLC Flow

**Status:** V0 conceitual

## 1. Escopo

AI-DLC Flow é um sistema de controle de contexto e fluxo para projetos assistidos por agentes. Ele não é waterfall: o lifecycle macro descreve o estado dominante da iniciativa, enquanto cada capability ou feature pode executar um ciclo menor.

O modelo é:

```text
Lifecycle → Artifact → Work Unit → Evidence → Gate → Metric → Forecast
```

Cada seta representa uma relação rastreável, não uma promoção automática.

## 2. Lifecycle

O lifecycle inicial é:

```text
Intent → Explore → Define → Design → Validate → Plan → Build → Verify → Release → Observe → Learn → Replan
```

### Significado das fases

| Fase | Pergunta dominante | Saída mínima |
|---|---|---|
| `Intent` | Que resultado humano/produto buscamos? | intenção, usuários, restrições, sucesso e perguntas abertas |
| `Explore` | O que sabemos e o que ainda precisamos descobrir? | mapa de domínio, fontes, hipóteses e riscos |
| `Define` | O que entra, não entra e sob quais regras? | escopo, requisitos, critérios e decisões pendentes |
| `Design` | Como a solução pode funcionar? | UX, domínio, arquitetura e contratos propostos |
| `Validate` | A proposta é aceitável e viável? | testes de hipótese, revisão, validação humana e limites |
| `Plan` | Qual trabalho ordenado pode ser executado? | work units, dependências, gates, risco e baseline |
| `Build` | O que será construído? | implementação versionada e registros de execução |
| `Verify` | O resultado atende aos critérios? | testes, revisão, evidências e defeitos classificados |
| `Release` | Pode ser disponibilizado neste ambiente? | autorização, versão, checklist e evidência de entrega |
| `Observe` | O que aconteceu depois da entrega? | sinais operacionais, uso, erros e feedback |
| `Learn` | O que deve mudar no produto ou no processo? | aprendizados confirmados e decisões de evolução |
| `Replan` | Qual é o próximo ciclo? | escopo/ordem atualizados e nova previsão |

### Transições

Uma transição requer:

1. estado atual conhecido;
2. artefatos mínimos da fase;
3. evidência correspondente ao risco;
4. gate satisfeito ou decisão humana explícita de exceção;
5. registro da decisão, responsável e próxima ação.

O fluxo pode voltar de qualquer fase para `Explore`, `Define`, `Design` ou `Plan` quando uma hipótese falhar, o escopo crescer ou a evidência contradizer o plano. Voltar é replanejamento, não falha do processo.

## 3. Artifacts

Artefato é um objeto versionado que carrega contexto para outra unidade ou fase. Tipos V0:

- `intent`: problema, resultado, usuários e restrições;
- `discovery`: fatos, fontes, hipóteses, riscos e perguntas;
- `requirement`: comportamento desejado e critérios verificáveis;
- `domain-model`: entidades, relações, invariantes e limites;
- `ux-design`: fluxo, estados, wireframe ou protótipo de interação;
- `architecture-decision`: alternativas, trade-offs e decisão;
- `test-plan`: cenários, dados, ambiente e resultado esperado;
- `work-plan`: work units, dependências, ordem, risco e gates;
- `prototype`: exploração de experiência, sem compromisso de produção;
- `poc`: prova técnica de uma hipótese delimitada;
- `implementation`: código, configuração ou infraestrutura versionada;
- `verification-report`: resultado reproduzível de testes/review/inspeção;
- `production-observation`: observação do sistema entregue em ambiente-alvo;
- `decision-record`: decisão humana ou exceção autorizada.

O tipo do artefato é declarado pelo autor e não muda por inferência do agente. Um protótipo não vira implementação porque contém código; uma implementação não vira evidência de produção porque foi mergeada.

## 4. Work unit

Work unit é a menor unidade que pode ser executada, verificada e aceita independentemente. Ela deve conter:

- `id`, título, objetivo e tipo de mudança;
- artefatos de entrada e saída esperados;
- owner e autoridade disponível;
- dependências e condição de desbloqueio;
- critérios de aceite e risco;
- estado, timestamps e eventos;
- evidências exigidas;
- gate de saída e próximo passo.

### Estados da work unit

```text
proposed → ready → in_progress → in_review → verified → accepted → released → observed → learned
                    ↘ blocked ↗                    ↘ rework ↗
```

- `proposed`: candidata, ainda sem prontidão;
- `ready`: critérios, entradas, owner e dependências disponíveis;
- `in_progress`: execução em curso, com WIP contabilizado;
- `blocked`: não pode avançar por dependência, decisão, permissão, ambiente ou evidência;
- `in_review`: resultado aguarda revisão apropriada;
- `rework`: evidência ou revisão exige alteração;
- `verified`: critérios técnicos verificados, sem declarar aceite de produto;
- `accepted`: gate humano/produto satisfeito;
- `released`: disponibilizada no ambiente autorizado;
- `observed`: sinais pós-entrega coletados;
- `learned`: aprendizado incorporado ou unidade fechada com próximo ciclo definido.

`done` não é estado universal: cada tipo de unidade termina no estado que sua política exige. Uma unidade pode ser `verified` sem ser `accepted` ou `released`.

## 5. Dependências, blockers e readiness

Dependência é relação declarada entre unidades ou artefatos. Blocker é impedimento atual que torna a unidade inelegível para avançar. Um risco possível não é blocker até impedir uma transição.

Readiness é uma decisão verificável, não um score subjetivo. Uma work unit está pronta quando:

1. objetivo e resultado estão claros;
2. entradas têm fonte e status;
3. critérios de aceite são observáveis;
4. dependências têm condição de desbloqueio;
5. owner e autoridade estão definidos;
6. dados, ambiente e ferramentas estão disponíveis;
7. gate de saída e evidência exigida estão definidos;
8. decisões humanas necessárias estão resolvidas ou explicitamente separadas.

Faltou qualquer item? Estado `proposed` ou `blocked`, com motivo e responsável. Não compensar lacuna com confiança do agente.

## 6. Traceability

A cadeia mínima é:

```text
Intent → Requirement → Design/Decision → Work Unit → Implementation → Verification → Gate → Release/Observation
```

Cada vínculo deve registrar `source`, `relation`, `status`, `owner` e, quando possível, `version`/`commit`/`timestamp`. Alterações de escopo devem apontar o que ficou obsoleto ou foi replanejado.

## 7. Commits não medem progresso

Commit mede uma operação de versionamento. Não prova que uma capability foi entregue, aceita ou opera. O progresso deve ser derivado de:

- work units aceitas/verificadas;
- gates satisfeitos;
- critérios rastreados;
- evidências reproduzíveis;
- observações pós-release.

Quantidade de commits, tokens ou linhas alteradas pode ser contexto auxiliar, nunca métrica principal de valor entregue.
