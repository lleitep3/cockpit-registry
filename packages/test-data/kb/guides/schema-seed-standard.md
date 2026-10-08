# test-data — schemas e seeds com evidência

Contexto: test-data; testes com dados sintéticos.

Schema observado vem do catálogo após migrations. Receita de geração é manual
e separada para preservar regras de domínio quando o schema evolui. FKs compostas
selecionam tuplas do mesmo pai, mantendo tenant. Reprodução exige seed, relógio,
versões e identidade das entradas; mesmo seed sozinho não basta.

Use a skill `schema-seed-qa` do pacote `test-data` e suas referências:
`references/pattern.md` para construção/evolução e `references/qa-workflow.md`
para verificação e curadoria. Templates de receita e relatório ficam nos assets
da skill e em `boilerplates/schema-seeds`.

Registrar resultado por capacidade: passou, falhou, não executado ou não suportado.
Aprovar extração não aprova geração. Consolidar causas/correções verificadas no KB
do projeto, sem copiar secrets ou dados reais. Isso melhora instruções/contexto
da IA; não é treinamento de pesos.

O pacote 0.4.0 inclui Massa CLI: `cockpit test-data schema inspect`, `validate` e
`generate`, além de `schema diff`. Dependências fixadas e runtime isolado via post-install. Gera JSONL
e manifesto; Comparação estrutural gera JSON e hashes, sem inferir renomeações. Sync de receitas
e carga no banco ainda não estão implementados.

Ambientes são referências a arquivo .env/export Postman, com banco esperado e
extração por tabela. Catálogo parcial mantém FKs externas. Mapear cenários de
pendência por regra real, destino exato e validação antes/depois na aplicação.
Carga/reset seguem pendentes; não inferir autorização a partir de uma consulta.
