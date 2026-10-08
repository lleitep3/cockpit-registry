# Workflow de QA e melhoria das instruções

## Preparar evidência

Registre revisão/ref do código quando disponível, versões do runtime, migrações
aplicadas, identidade não sensível do ambiente e arquivos de entrada. Enumere as
capacidades sob teste. Use o modelo `../assets/qa-report.md` sem marcar o que não rodou.

## Verificar schema

- Consultar banco com autenticação e snapshot somente leitura.
- Comparar tabelas/colunas e FKs com o catálogo; confirmar ordem das FKs compostas.
- Verificar defaults, identity/generated, checks e índices parciais/expressões.
- Extrair duas vezes sem mudança e comparar conteúdo; anotar diferenças esperadas.
- Testar schema inexistente, destino já existente, erro de conexão sem vazamento de
  segredo e tabelas excluídas. Não executar teste de falha em produção.
- Se objeto não é suportado, registrar impacto e não aprovar cobertura completa.

## Verificar seeds quando houver motor

- Validar receita antes de gerar. Checar referências, domínio de unicidade, pesos,
  estratégia para ciclos e restrições entre campos.
- Repetir geração com mesmas entradas fixadas e comparar conforme manifesto.
- Validar contagens, PK/unique, FKs compostas, tenant e regras de negócio explícitas.
- Carregar em banco descartável autorizado com as mesmas migrations e constraints.
  Comprovar aceitação/rejeição de cada cenário. Não executar seeds de identidade
  externa como parte de fixture estrutural sem necessidade/autorização.
- Verificar repetição/idempotência e comportamento após falha, preservando evidência.
- Avaliar volume/desempenho apenas conforme alvo do projeto; não inventar SLA.

## Resultado por capacidade

Use `passou`, `falhou`, `não executado` ou `não suportado`, com evidência vinculada.
Uma falha impede aprovação da capacidade afetada; extração pode passar enquanto
geração permanece não implementada. Não transformar um checklist preenchido em
prova de validação. Informe risco restante e próxima verificação concreta.

## Consolidar melhoria da IA

Para falha reproduzível: contexto → comportamento observado → causa → correção →
verificação → regra aplicável → limites. Para decisão verificada, registre motivos
e condições em que deve ser reconsiderada. Use uma entrada por assunto durável.

Busque entrada existente no KB. Atualize preservando conhecimento válido ou crie
no contexto correto. Confirme caminho/ID e recuperação por busca antes de dizer
que salvou. Não guardar outputs brutos, secrets ou cada status de execução.

Atualizar skill/referências exige evidência que justifique a mudança. Revalidar a
skill e seus links e executar testes afetados. Isso é curadoria de contexto,
não aprendizado automático dos pesos do modelo. Não agendar QA sem solicitação.
