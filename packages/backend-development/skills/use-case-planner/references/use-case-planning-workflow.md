# Workflow reproduzível de planejamento de caso de uso

Este documento define o formato mínimo para uma sessão de planejamento. Ele
deve ser adaptado ao domínio, mas os identificadores e as relações precisam ser
preservados para que app, API, design e testes falem sobre a mesma fatia.

## Pacote documental

### 1. Documento principal do fluxo

Nome sugerido: `FLOW-001-UC-001-nome-curto.md`.

```markdown
# FLOW-001 — Nome do fluxo

**Caso de uso:** UC-001 — Nome do caso de uso
**Status:** draft | ready_for_review | accepted | superseded
**Escopo:** app | API | app_and_api

## 1. Ator e objetivo

## 2. Pré-condições

## 3. Fluxo principal

## 4. Fluxos alternativos e exceções

## 5. Estados antes e depois

## 6. Regras de autorização

## 7. Eventos de auditoria

## 8. Request/response da API

## 9. Cenários permitidos e negados

## 10. Dados fictícios fixos

## 11. Critérios de aceite

## 12. Telas correspondentes no app

## Decisões aceitas

## Perguntas abertas
```

### 2. Plano de testes

Nome sugerido: `FLOW-001-UC-001-test-plan.md`.

Cada cenário deve informar fixture, pré-condição, ação, resultado observável e
evento de auditoria esperado quando aplicável.

```gherkin
Scenario: resultado permitido
  Given <fixture e pré-condições>
  When <ação do ator>
  Then <estado e resposta observáveis>
  And <auditoria esperada>
```

Inclua pelo menos:

- caminho principal permitido;
- cada papel ou escopo negado;
- recurso inexistente;
- estado inválido ou transição repetida;
- dados inválidos e limites;
- consulta sensível auditada;
- idempotência quando a ação puder ser repetida.

### 3. Diagrama opcional

Nome sugerido: `FLOW-001-UC-001-flow.mmd` ou um fluxo equivalente no Figma.

O diagrama deve usar os mesmos nomes de estados, atores e IDs do documento
principal. Um protótipo visual não substitui as pré-condições, regras ou testes.

### 4. Contrato inicial da API

Nome sugerido: `FLOW-001-UC-001-api.md`.

Defina apenas os endpoints necessários para a fatia:

- método e rota;
- autenticação e autorização;
- request válido;
- response de sucesso;
- erros esperados;
- transação e efeitos observáveis;
- auditoria;
- idempotência e concorrência, quando relevantes.

O contrato não deve inventar campos que não estejam justificados pelo fluxo.

## Reprodutibilidade

Use fixtures estáveis e fictícias. Documente pelo menos:

- IDs fixos de usuário, paciente, sessão e formulário;
- perfil, vínculos e especialidade de cada usuário;
- datas relativas ou relógio congelado;
- timezone;
- estado inicial do banco;
- ordem das ações;
- resultado esperado após cada ação.

Não use dados clínicos reais. Não dependa de cliques implícitos, horário atual,
ordem acidental de registros ou estado persistido de outra execução.

## Matriz de rastreabilidade

| Elemento | Documento | API | App/Figma | Teste |
| --- | --- | --- | --- | --- |
| Ator e objetivo | `FLOW-*` | autorização | tela de entrada | cenário permitido |
| Estado | `FLOW-*` | response/transição | estado visual | transição |
| Regra de acesso | `FLOW-*` | policy/guard | ação visível | cenário negado |
| Auditoria | `FLOW-*` | evento | confirmação quando necessária | evento esperado |
| Critério de aceite | `FLOW-*` | efeito observável | resultado visual | teste de aceite |

## Gate de saída

A sessão termina com uma decisão explícita:

- `accepted`: pode virar trabalho de implementação;
- `ready_for_review`: falta revisão de produto, clínica ou arquitetura;
- `blocked`: há uma dependência externa ou decisão necessária;
- `superseded`: foi substituído por outro fluxo.

O entregável deve listar o próximo passo, responsável e documentos que precisam
ser atualizados quando uma pergunta aberta for respondida.
