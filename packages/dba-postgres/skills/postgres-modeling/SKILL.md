---
name: postgres-modeling
description: Revisa modelos físicos PostgreSQL, cardinalidades, integridade, isolamento por tenant, histórico e migrations. Use antes de implementar tabelas ou revisar DER; não inventa relações nem executa mudanças de schema.
---
# Modelagem PostgreSQL

Leia [workflow de modelagem](../dba-postgres/references/model-review.md) e
`~/.cockpit/packages/dba-postgres/kb/guides/postgres-modeling.md`.

Comece por requisitos aceitos, estados e consultas críticas. Compare três objetos:
modelo de negócio, migrations versionadas e schema realmente observado. Rotule
cada entidade como existente, proposta ou incompatível; não desenhe proposta como fato.

Revisar identidade, cardinalidade e nulabilidade; limites transacionais; histórico
versus estado atual; unicidade parcial; cascatas/retenção; autorização versus FK;
concorrência e escopo de tenant. Evitar JSON genérico para relações que exigem FKs.
Não multiplicar tabelas nem desnormalizar sem necessidade verificável.

FK composta com tenant pode justificar UNIQUE adicional. Uma tabela de IDs não
prova que o cadastro inteiro existe. Exigir migrations e testes de invariantes,
concorrência e isolamento para implementação. Articular backfill, compatibilidade
e rollback antes da migração. Usar api-developer ao implementar o consumidor.
