# Autonomia e fronteiras de extensão

## 1. Princípios

- Autonomia é autorização contextual, não personalidade do agente.
- Escopo, dados, ferramentas, custo e mutações permitidas devem estar explícitos.
- Agente deve parar diante de decisão humana, evidência ausente, ambiguidade ou duas tentativas sem progresso.
- Toda ação relevante deixa resultado reproduzível e handoff.
- A automação pode acelerar o fluxo; não pode transformar hipótese em fato.
- O sistema deve preferir inspeção e proposta antes de mutação externa.

## 2. Classificação

| Forma | Fronteira | Exemplos V0/V1 |
|---|---|---|
| `Skill` | transformação delimitada e reutilizável | classificar evidência, derivar critérios, validar readiness |
| `Workflow` | sequência previsível com ordem e gates | bootstrap, inception, feature-cycle, release, project-control |
| `Agent` | responsabilidade contextual que compõe várias skills | Product, Architecture, QA, Project Controller |
| `Gate` | regra de passagem, não executor | scope aprovado, readiness, verify, release |
| `Human decision` | escolha de produto, risco ou política | escopo, fórmula clínica, privacidade, aceite, release |

Não criar um agente para cada atividade. Se a tarefa é determinística e reutilizável, começa como skill ou check. Se é sequência estável, workflow. Agent só quando precisa interpretar contexto, negociar trade-offs e decidir quais skills aplicar dentro de uma autoridade limitada.

## 3. Oportunidades priorizadas

| Prioridade | Nome proposto | Forma | Motivo |
|---|---|---|---|
| P0 | `classify-evidence` | Skill | evita promoção indevida e cria proveniência |
| P0 | `check-readiness` | Skill + Gate | transforma lacunas em blockers explícitos |
| P0 | `bootstrap-project` | Workflow | cria estrutura mínima, fontes, estado e auditoria |
| P1 | `capture-intent` | Skill | separa pedido inicial de especificação |
| P1 | `derive-requirements` | Skill | gera candidatos ligados às fontes, sem aprovação automática |
| P1 | `discover-domain` | Agent | interpreta contexto e coordena descoberta com perguntas humanas |
| P1 | `decompose-work` | Skill | transforma requisitos aceitos em work units e dependências |
| P1 | `inspect-progress` | Skill | calcula inventário e métricas a partir de eventos |
| P1 | `project-control` | Agent + Workflow | prioriza fila, blockers, forecast e replan sob política |
| P2 | `challenge-spec` | Agent/Review | procura ambiguidades, riscos e critérios ausentes |
| P2 | `design-feature` | Agent | compõe UX, domínio e arquitetura quando houver decisão contextual |
| P2 | `create-test-plan` | Skill | deriva cenários e negativos a partir de critérios |
| P2 | `estimate-work` | Skill | aplica método explícito e faixas calibradas |
| P3 | `construction-cycle` | Workflow | implementação, testes, review e evidência |
| P3 | `release-observe-learn` | Workflow | release controlado, observação e replan |

Os nomes são proposta V0; a fronteira deve ser revista após observar uso real no Partilhar e no Workout App.

## 4. Project Controller futuro

O Project Controller não deve escrever requisitos clínicos nem aprovar release. Sua responsabilidade é manter o estado operacional: ler fontes, detectar inconsistências, atualizar o inventário de work units, apontar blockers, calcular métricas, gerar forecast e pedir decisões humanas. Toda mudança de escopo deve voltar pelo gate apropriado.
