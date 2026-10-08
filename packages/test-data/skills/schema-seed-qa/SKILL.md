---
name: schema-seed-qa
description: Criar, evoluir e revisar schemas extraídos de bancos e seeds sintéticos reproduzíveis para testes, consolidando evidências de QA e aprendizados verificados.
---

# Schemas e seeds com QA

Use em extração de catálogo, receitas de dados fictícios, evolução de schemas e
QA dessas entregas. Localize o projeto e seu contrato; não pressupor que o exemplo
Partilhar ou o caminho do Massa sejam o destino de toda tarefa.

## Contrato obrigatório

- Consulte o KB antes do trabalho. Leia o estado real do CLI e as migrations.
- Extraia estrutura do banco escolhido após migrations; mantenha `schema.yaml`
  separado de `generation.yaml`. Não sobrescreva regras manuais durante sincronização.
- Preserve FKs compostas, tenant e constraints. Nomes sugerem providers, não
  comprovam regras de negócio. Checks e triggers não interpretados são limitações.
- Registre seed, relógio fixo, versões e identidade do schema/receita para reprodução.
- Nunca inclua URL de conexão, credenciais ou registros reais nos artefatos de QA.
- Execute apenas as mutações autorizadas. Extração usa consulta somente leitura;
  load de seeds precisa de destino e escopo autorizados. Excluir dados não é implícito.
- Distinga implementação funcional, contrato proposto e comportamento não testado.

## Execução

Ao criar ou atualizar, leia [padrão](references/pattern.md). Ao verificar entrega ou
consolidar evidências, leia [workflow de QA](references/qa-workflow.md).

Entregue artefatos revisáveis, comandos realmente executados, resultados e limites.
Use os modelos em `assets/` quando cabíveis; adapte ao projeto sem inventar evidência.
Não declare aprovação de seeds apenas porque a extração de schema passou.

## Aprendizado para próximas execuções

Após QA, registre problema observado, causa confirmada, correção e teste de regressão
relevante. Inclua condições de aplicação e fonte da evidência. Hipóteses ficam
identificadas, sem virar regra geral. Busque duplicatas antes de adicionar/atualizar
o KB no contexto do projeto; confirme persistência e recuperação por busca.

Melhore esta skill somente com evidência reutilizável. Isso melhora o contexto e
as instruções da IA; não significa treinamento ou alteração dos pesos do modelo.
Não criar agente paralelo, automação ou comunicação externa por consequência do QA.
