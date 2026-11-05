# Projeto de seeds — carga restrita, 0.5.0

Status: implementado em Massa CLI; reset/up/init/importação e assertions de domínio ainda não implementados.

Um projeto YAML seleciona cenários JSONL gerados pelo CLI. O banco deve estar migrado e o schema extraído deve ser completo nos metadados das tabelas selecionadas. A conexão vem do environment registrado (.env ou export Postman); credenciais não entram no projeto. Environment writable e confirmações explícitas são exigidos na aplicação, não na leitura.

```yaml
version: 1
name: exemplo_qa
schema_file: schema.yaml
scenarios:
  base:
    bundle: data/base
    scope:
      clientes: {clinic_id: seed_clinic}
      pedidos: {clinic_id: seed_clinic}
```

Schema e bundles ficam dentro do diretório do projeto; paths e symlinks que escapam são recusados. Cada tabela gerada deve declarar escopo não vazio por igualdade de colunas. Todos os registros precisam obedecer ao escopo e fornecer PK explícita. Fixar clinic_id na receita e preservar a FK composta nos filhos; escopo não comprova que o tenant é descartável nem substitui autorização do destino.

1. Extrair schema pós-migrations para schema.yaml, ajustar receita e gerar bundle com manifest.json. Metadados resumidos escritos à mão não satisfazem a comparação com catálogo real.
2. Preparar plano somente leitura:

```bash
cockpit test-data seed plan --project seed-project.yaml --scenario base \
  --environment local --registry environments.yaml --output plan.json
```

O plano contém escopo, inserções/reuso por tabela, identidade do servidor/banco/papel, hashes de entradas e catálogo. Revisar YAML, receita, constraints/triggers e plano. O CLI imprime o hash de confirmação do plano. Não copiar credenciais ao argumento.

3. Aplicar com plano revisado, nome exato do banco e hash impresso (substituir BANCO e HASH):

```bash
cockpit test-data seed apply --project seed-project.yaml --scenario base \
  --environment local --registry environments.yaml --plan plan.json \
  --confirm BANCO --confirm-plan HASH --output receipt.json
```

4. Conferir somente leitura depois:

```bash
cockpit test-data seed verify --project seed-project.yaml --scenario base \
  --environment local --registry environments.yaml --output verification.json
```

Saídas precisam de caminho novo. Mudança de inputs, catálogo, banco, papel ou contagens exige novo plano e revisão. Depois de aplicar, o plano antigo passa a estar desatualizado: gerar novo plano para repetição; registros idênticos aparecem como reuse. O loader nunca faz update/delete nem usa ON CONFLICT para esconder diferença. Mesmo PK com valores fornecidos diferentes falha; colunas omitidas são responsabilidade dos defaults do banco e não entram nessa equivalência.

## Transação, concorrência e recuperação

A carga usa transação repeatable-read, locks SHARE ROW EXCLUSIVE nas tabelas em ordem estável e timeouts de lock/statement. Locks bloqueiam outras escritas nessas tabelas durante a operação; usar volumes modestos e ambiente de teste autorizado. O plano é recalculado depois dos locks. Inserções, constraints imediatas/diferidas e comparação de todos os valores fornecidos passam antes do commit; falha reverte a transação. Não cria tabelas de controle nem altera schema/migrations.

Recibo em arquivo é escrito após o commit e não participa da transação PostgreSQL. Se a conexão falhar na confirmação ou o arquivo não puder ser escrito, o resultado pode ser desconhecido: executar verify/plan novamente, reconciliar o banco e gerar novo plano. Não presumir rollback nem repetir cegamente o plano antigo. Triggers/funções/defaults podem ter efeitos externos ou sequências não reversíveis; revisar esses efeitos antes de aplicar. O loader não é sandbox de SQL existente.

Limites: até 100 mil registros/64 MiB por arquivo; ordem segue o manifesto; PKs repetidas, hash inválido, escopo divergente, identidade always/campos generated e valores compostos são recusados. Constraints e tenant são aplicados pelo banco; funções/RLS e permissões de domínio não são certificadas pela comparação de catálogo. Exatamente as colunas fornecidas são verificadas, sem apagar registros extras do ambiente.

Carga direta é fixture de banco, não operação clínica da aplicação. Autoria/auditoria, readiness, fila, deep-links e UI precisam de adaptador/casos de uso e testes autenticados do Partilhar. Os quatro pacientes do FLOW-017 seguem especificados, não injetados. Nenhuma identidade Cognito é criada. Importação de dados reais tem contrato próprio e não usa este comando como autorização de migração.
