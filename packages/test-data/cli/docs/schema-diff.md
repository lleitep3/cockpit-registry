# Comparação estrutural de schemas

Massa CLI 0.3.0 adiciona `schema diff --before schema.yaml --after schema-next.yaml`.
A saída JSON contém `changed`, alterações por caminho e hashes SHA-256 das entradas.
Use `--output diff.json` para arquivo novo. `--fail-on-change` retorna 2 no CLI
quando houver drift; erros retornam 1. O Cockpit instalado preserva esses códigos, verificado em execução real.

Compare nova extração após migrations com schema versionado. Revise o relatório,
valide a receita contra novo schema, ajuste regras manualmente e gere nova massa.
Versione schema, receita e evidência de QA na mesma mudança revisável.

Coleções de constraints, índices, triggers e enums usam nome como identidade.
Ordenação da lista dessas coleções não cria ruído; ordens de tupla FK, campos e
valores enum são significativas. Source.server_version é ignorado, restantes
metadados são comparados. Mudança em comentário também aparece. Não é análise de
compatibilidade SQL, backup, migração, nem sync de regras de domínio.

Catálogos podem ter nomes internos e definições SQL: o relatório compartilha esses
metadados. Revisar antes de publicar. Receitas, arquivos de entrada e banco não
são alterados. Arquivo de saída existente é recusado.
