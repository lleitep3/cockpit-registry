# Laboratório local de DBA PostgreSQL

PostgreSQL 17.11; pgAdmin 9.18 opcional. Para desenvolvimento e ensaios com dados
sintéticos/sanitizados, não produção. Recursos locais: banco até 1 CPU/1 GiB,
pgAdmin até 1 CPU/512 MiB, além do Docker. Rever limites para cargas representativas.

## Subir

Gerar uma pasta nova a partir do pacote instalado:

```sh
cockpit dba-postgres lab-init --output ./meu-lab
cd meu-lab
docker compose config --quiet
docker compose up -d --wait db
```

lab-init cria .env público e senhas aleatórias em .secrets/. Pastas ficam 0700;
a senha PostgreSQL fica 0600. O arquivo pgAdmin fica 0444 para leitura pelo UID 5050
do container, protegido no host pelas pastas 0700. Nunca exibe
senhas nem sobrescreve pastas. .gitignore exclui secrets, backups e evidências.
Arquivos de secret locais não são um vault criptografado. Não os versionar.

Porta padrão: 127.0.0.1:55432. Banco lab; usuário lab_admin. O usuário é administrador
do laboratório: não usar suas credenciais na aplicação. Crie roles de aplicação,
migration e observação com privilégios apropriados antes de integrar consumidores.
Healthcheck indica disponibilidade do servidor, não valida senha nem migrations.

O terminal administrativo usa o psql do container; não exige psql no host:

```sh
docker compose exec db sh -c 'exec psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

## Interface opcional

```sh
docker compose --profile tools up -d --wait
```

Abrir http://127.0.0.1:55080. Login conforme PGADMIN_EMAIL em .env; consultar a senha
localmente em .secrets/pgadmin_password, sem enviá-la para chat/log. Registrar servidor:
host **db**, porta **5432**, banco lab, usuário lab_admin e senha em
.secrets/postgres_password. Não usar localhost como host dentro do pgAdmin.
Se alterar .env, ajustar o cadastro conforme os novos valores.

HTTP e PostgreSQL sem TLS são restritos ao loopback neste laboratório. Não expor
portas em 0.0.0.0 nem usar o exemplo como baseline de produção. Acesso por outro host
exige projeto próprio de TLS, autenticação e rede.

## Exercício de backup e restauração

Usar somente dumps confiáveis: restauração pode executar código contido no backup.
No shell da pasta do lab, escolher um nome novo de arquivo e manter .gitignore:

```sh
mkdir -p backups
chmod 700 backups
(umask 077; set -C; docker compose exec -T db sh -c 'exec pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > backups/lab-01.dump)
```

Exigir código zero antes de confiar no arquivo. Em falha ele pode estar incompleto;
preservar para diagnóstico e escolher outro nome no retry. Não restaurar sobre lab.
Criar destino novo (o comando falha se já existir) e restaurar:

```sh
docker compose exec -T db sh -c 'exec createdb -U "$POSTGRES_USER" --template=template0 lab_restore_01'
docker compose exec -T db sh -c 'exec pg_restore -U "$POSTGRES_USER" --dbname=lab_restore_01 --exit-on-error --no-owner --no-privileges' < backups/lab-01.dump
```

Comparar tabelas, constraints, contagens e invariantes conhecidas; executar smoke das
consultas. Este ensaio lógico não valida PITR, roles globais, RPO/RTO de produção
ou recuperação em outro host. Consultar workflow recovery.md do pacote.

## Evidência usando o cliente do container

O SQL fixo não precisa de credenciais de produção. Em shell da pasta do lab:

```sh
mkdir -p evidence
(umask 077; set -C; cockpit dba-postgres sql | docker compose exec -T db sh -c 'exec psql -X -w -qAt -v ON_ERROR_STOP=1 -v schema=public -U "$POSTGRES_USER" -d "$POSTGRES_DB"' > evidence/baseline.json)
cockpit dba-postgres analyze evidence/baseline.json --output evidence/report-01
```

Habilitar pipefail no shell se disponível e conferir códigos de saída de ambos os
comandos antes de considerar a coleta válida. Conteúdo JSON é validado pelo analyze.

## Persistência e parada

```sh
docker compose stop
# Para reiniciar os mesmos dados:
docker compose up -d --wait db
# Remover containers/rede preservando volumes, quando desejado:
docker compose --profile tools down
```

Não usar down -v como rotina: remove dados. Remoção de volumes precisa ser uma ação
explícita após decidir o destino dos dados. Mudar senha no arquivo ou variáveis de
init não altera um banco já inicializado; fazer rotação planejada no banco e clientes.
O pgAdmin também conserva seu estado no volume após inicialização.

Não trocar a major da imagem sobre o volume existente. PostgreSQL 18 muda convenções
do diretório de dados da imagem oficial; use novo laboratório e workflow de upgrade.
Tags com patch são legíveis, mas podem ser reconstruídas; pin por digest quando a
reprodutibilidade exigir. Nunca atualizar automaticamente um volume para outra major.

Fontes: [imagem PostgreSQL](https://hub.docker.com/_/postgres),
[pgAdmin](https://www.pgadmin.org/docs/pgadmin4/latest/container_deployment.html),
[Compose/healthcheck](https://docs.docker.com/compose/how-tos/startup-order/).
