# PostgreSQL: acessos e proteção de dados

Contexto: dba-postgres. Revisado em 2026-09-28; referência PostgreSQL 17.

Separar owner, migration, runtime, observação e administração. Um usuário de aplicação
não deve herdar superuser por conveniência. Examinar PUBLIC e privilégios futuros junto
com grants atuais; não assumir que schema isolado é fronteira de autorização.

HBA seleciona a primeira regra correspondente, sem fallback por falha de autenticação.
Revisar origem, banco, usuário e tipo de conexão antes de editar. TLS exige política
coerente de certificados; arquivo secreto local não equivale a vault criptografado.
[HBA](https://www.postgresql.org/docs/17/auth-pg-hba-conf.html).

RLS tem comportamento distinto para owners e roles privilegiadas. Testes precisam usar
a identidade real do consumidor. FKs e constraints não substituem autorização de leitura.
[RLS](https://www.postgresql.org/docs/17/ddl-rowsecurity.html).

Auditoria e backups contêm informação sensível. Definir finalidade, acesso e retenção;
não despejar dados/SQL com literais em ferramentas externas. Default privileges e
funções SECURITY DEFINER merecem revisão específica de ownership e search_path.
A análise deve evidenciar riscos reais, sem declarar conformidade jurídica.
