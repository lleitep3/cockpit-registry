# PostgreSQL: modelagem e integridade

Contexto: dba-postgres. Revisado em 2026-09-28; referência PostgreSQL 16.

Começar por invariantes: quem pode existir sem quem, quais estados são incompletos,
o que pode se repetir, quando um vínculo termina e qual histórico precisa sobreviver.
Criar uma estrutura relacional que represente essas decisões e consultas previstas.
Separar autenticação de cadastro quando pessoas não precisam de login.

PK/UNIQUE criam índices; FK não cria automaticamente índice do lado referenciador.
NOT NULL e CHECK resolvem problemas diferentes; CHECK com resultado nulo não rejeita
por si só o registro. CHECK não deve depender de outras linhas/tabelas para impor
integridade. Usar restrições apropriadas e transação/concorrência para regras compostas.
[Constraints PostgreSQL 16](https://www.postgresql.org/docs/16/ddl-constraints.html).

Em sistemas por clínica/tenant, UNIQUE(tenant_id,id) com FK composta pode ser proposital
mesmo com PK(id). Revisar antes de considerar redundância. Isso protege referências,
não substitui autorização. Auditar acessos e testar cross-tenant separadamente.

Soft delete altera unicidade vigente, consultas, retenção e cascatas. Índices parciais
não representam unicidade histórica global. Evitar normalizar ou usar JSONB apenas por
preferência: documentar consultas, validação, mutabilidade e índices de cada alternativa.

Cadastro progressivo precisa de invariantes por estado: rascunho e concluído não são
sinônimos. Planos com vigência devem explicitar versões, início/fim, timezone, capacidade
e semântica de agenda semanal; não materializar recorrência indefinidamente.

Entrega: modelo proposto separado do atual; migration; backfill se houver;
testes de constraints, concorrência, tenant e compatibilidade; estratégia de recuperação.
