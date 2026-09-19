# Evidência, gates e autoridade

## 1. Separar artefato de evidência

Um artefato declara ou materializa algo. Evidência mostra o que foi observado, como foi observado, em qual versão e com qual limite. O mesmo arquivo pode ser evidência da existência daquele arquivo, mas não de todo comportamento que ele descreve.

Regra central:

```text
Specification != Prototype != POC != Implementation != Production Evidence
```

### Classes que não podem ser promovidas implicitamente

| Classe | O que prova | O que não prova |
|---|---|---|
| `Specification` | intenção, regras e critérios registrados | que a solução foi implementada ou aceita |
| `Prototype` | interação/experiência explorada em escopo de demonstração | arquitetura de produção, persistência ou segurança |
| `POC` | viabilidade técnica de uma hipótese delimitada | completude, qualidade operacional ou pronto para release |
| `Implementation` | mudança versionada no código/configuração | que passou em todos os critérios ou funciona em produção |
| `Production Evidence` | comportamento observado em ambiente-alvo, versão identificada e cenário registrado | validade fora do cenário, ausência de risco futuro ou aceitação clínica automática |

Uma Figma screen é `ux-design`/`prototype` conforme o registro do trabalho; não é UI implementada. Um teste verde é evidência de seu cenário e versão; não é evidência de uso clínico ou produção.

## 2. Níveis de assurance da evidência

O tipo e o nível são campos separados.

| Nível | Nome | Requisito mínimo |
|---|---|---|
| `E0` | ausente | nenhuma observação verificável |
| `E1` | declarada | autor, afirmação e fonte; não suficiente para gate técnico |
| `E2` | observada | inspeção/execução registrada em versão identificada |
| `E3` | reproduzível | comando, ambiente, dados, resultado e limite permitem repetir |
| `E4` | revisada | revisão independente ou validação humana apropriada ao risco |
| `E5` | operacional | observação pós-release no ambiente-alvo, com janela e sinal definidos |

`E1` não transforma uma declaração em fato. O nível máximo depende do cenário: um teste unitário pode ser `E3` para uma regra e continuar sem evidência da operação end-to-end.

## 3. Registro mínimo de evidência

```yaml
id: EV-0001
kind: verification
level: E3
claim: "pontuação é calculada conforme a regra da versão"
source_artifact: REQ-0004
subject: WU-0012
version: "commit ou versão do artefato"
scenario: "dados sintéticos descritos"
command_or_method: "comando, inspeção ou procedimento"
result: pass|fail|partial|unknown
limits:
  - "o que não foi coberto"
recorded_at: "timestamp"
recorded_by: "actor"
```

Não incluir prompts, segredos, dados reais de pacientes ou logs brutos em evidência pública.

## 4. Gates

Gate é uma regra de passagem. Deve ter condição objetiva, evidência exigida, autoridade e saída possível.

| Gate | Verifica | Autoridade padrão |
|---|---|---|
| `G-INTENT` | problema, resultado, usuários, restrições e perguntas explícitos | humano/produto |
| `G-SCOPE` | escopo incluído/excluído e prioridade aprovados | humano/produto |
| `G-DOMAIN` | cenários, entidades e invariantes sustentados por fontes | humano + agente como análise |
| `G-DESIGN` | UX/arquitetura/contratos coerentes e riscos conhecidos | humano para decisão, agente para consistência |
| `G-READINESS` | work units executáveis, dependências e critérios observáveis | agente pode verificar; humano resolve exceções |
| `G-BUILD` | implementação compilável/testável e evidência E3 apropriada | agente/CI, com política do projeto |
| `G-VERIFY` | critérios, negativos, regressões e revisão cobertos | QA/agent + aprovação humana quando exigida |
| `G-RELEASE` | risco, privacidade, versão, rollback e autorização | humano responsável |
| `G-OBSERVE` | sinais operacionais e feedback coletados | agente mede; humano interpreta impacto |
| `G-REPLAN` | aprendizado convertido em decisão ou nova work unit | humano para mudança de escopo |

Estados do gate: `open`, `ready_for_review`, `passed`, `failed`, `waived_by_human`, `superseded`. `waived_by_human` exige motivo, responsável, risco aceito e prazo de revisão; não é equivalente a `passed`.

## 5. Decisão humana versus automação

### Humano deve decidir

- intenção e resultado do produto;
- escopo e prioridade;
- regras clínicas, interpretação de pontuação e conteúdo sensível;
- trade-offs de arquitetura com impacto relevante;
- privacidade, segurança, retenção e compliance;
- aceite do usuário/stakeholder;
- autorização de release, exceção ou mudança de risco.

### Agente pode executar/verificar

- inventário de arquivos, links, manifests e estados;
- validação de schema e consistência referencial;
- derivação de candidatos com proveniência explícita;
- decomposição proposta, dependências e detecção de blockers;
- execução de testes autorizados;
- cálculo de métricas a partir de eventos;
- intervalos de forecast quando os dados e a política estão disponíveis;
- relatório de lacunas e pedido de decisão.

Agente pode recomendar uma decisão. Não pode registrá-la como aprovada por silêncio, inferência ou sucesso técnico.
