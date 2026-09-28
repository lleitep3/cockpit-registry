# PostgreSQL: evidência antes de otimização

Contexto: dba-postgres. Revisado em 2026-09-28. Aplicabilidade técnica: PostgreSQL 16;
confirmar catálogo e documentação da versão alvo antes de reutilizar.

## Método

Cada recomendação registra: fato observado, fonte/instante/janela, hipótese, confiança,
limitações, experimento, benefício esperado, risco e critério de rollback. Não confundir
modelo desejado com schema existente. Uma tabela contendo só IDs não entrega um cadastro.
DER comprova relações declaradas; não expressa todas as regras clínicas/de negócio.

Contadores são cumulativos, podem atrasar e podem ser resetados. Deltas precisam de
mesma origem e janela, sem resets/recriação. Permissões restringem observabilidade;
nulos ou ausência não provam saúde. O pacote coleta um snapshot, não calcula taxas.
[Estatísticas PostgreSQL 16](https://www.postgresql.org/docs/16/monitoring-stats.html).

## Lições generalizadas de revisão de um MVP

Um catálogo de duas dezenas de tabelas pode ocupar menos de um MiB e ainda representar
responsabilidades distintas. Contagem de tabelas não mede custo. Separar domínio,
auditoria, prévias e idempotência antes de discutir retenção ou consolidação.
Vínculo vigente e histórico requerem regras diferentes; uma unicidade parcial não
transforma todo o histórico em relação 1:1. IDs de recursos polimórficos sem FKs não
viram relações inventadas. Não armazenar evidência operacional de cliente neste pacote.

## Privacidade e evidência

Mesmo nomes de tabelas/colunas podem revelar o domínio. Arquivos locais ficam privados;
revisão humana/agente antes de commit. O coletor exclui registros, query text, planos,
comentários, defaults e definições com possíveis literais. Não é um anonimizador geral.
Erros brutos de conexão não devem aparecer em logs; corrigir acesso via perfil explícito.
