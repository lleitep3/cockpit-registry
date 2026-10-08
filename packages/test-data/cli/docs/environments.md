# Ambientes PostgreSQL por referência — Massa CLI 0.4.0

Conexão não é argumento do shell. Guarde DATABASE_URL em arquivo .env privado ou
export de environment do Postman. Adicione ambos ao .gitignore. O registro YAML
contém referência ao arquivo, variável, banco esperado, schema e permissões; não
copia senha, token, connection string ou outras variáveis do Postman.

```sh
cockpit test-data environment add --name local --env-file .env.seed --database meu_banco --registry environments.yaml
# Alternativa: export JSON do environment Postman contendo DATABASE_URL
cockpit test-data environment add --name dev --postman dev.postman_environment.json --connection-env DATABASE_URL --database meu_banco_dev --registry environments.yaml
cockpit test-data schema inspect --environment local --registry environments.yaml --output schema.yaml
cockpit test-data schema inspect --environment local --registry environments.yaml --table patients --output patients.schema.yaml
# Repetir --table para mais de uma tabela, com metadados e FKs preservados
cockpit test-data schema inspect --environment local --registry environments.yaml --table patients --table patient_guardians --output patient-registration.schema.yaml
```

O nome do banco na conexão deve ser igual a --database. .env usa valores literais,
sem interpolação de variáveis herdadas. Postman usa uma única variável habilitada
com valor resolvido; placeholders {{...}} e secrets não exportados precisam ser
resolvidos no arquivo privado. Nome do ambiente usa letras/números/underscore.
Referências são relativas ao arquivo de registro, não ao diretório de execução.
Ambiente existente é recusado; editar cadastro é uma mudança revisável.

Sem flags, writable=false e resettable=false. Esses campos preparam a política de
futura carga/reset; esta versão só cadastra e lê o catálogo. --writable/--resettable
não implementam mutações. Extração continua em transação somente leitura com
timeouts. Conexões remotas podem ser utilizadas para leitura quando autorizadas.
Não existe seleção automática por ambiente herdado.

--schema pode selecionar outro schema no ambiente, preservando a conexão/banco.
Tabela inexistente ou excluída falha; não retorna catálogo vazio silenciosamente.
Extração parcial mantém FKs para pais fora da seleção; não inventa registros nem
inclui pais automaticamente. Schema parcial sozinho pode não bastar para gerar
receita coerente: incluir pais ou documentar fixture/lookup futuro.

Para validar evolução: extraia novo arquivo e execute schema diff --before arquivo
versionado --after nova-extração --fail-on-change. Para validar receita use validate
--schema arquivo --recipe generation.yaml. Não confundir checks estruturais com
regras de domínio da aplicação.

Registro salvo com permissão 0600 e sem segredo. Credenciais permanecem sob as
permissões do arquivo de origem; a ferramenta não amplia permissões nem importa
tokens API. Export de Postman é um formato de entrada, não execução de requests.
Carga, reset, projeto de seed e validação HTTP ainda estão em evolução.
