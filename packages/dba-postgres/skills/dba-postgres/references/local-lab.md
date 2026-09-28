# Workflow: laboratório de DBA

1. Escolher pasta nova e portas livres; `cockpit dba-postgres lab-init --output PASTA`.
2. Revisar .env (sem senhas), compose.yaml e README gerados. Conferir major da imagem.
3. Executar compose config --quiet e subir db com --wait. pgAdmin usa profile tools.
4. Validar conexão TCP autenticada além do healthcheck; não copiar senha para logs.
5. Criar dados sintéticos; testar persistência após restart, dump e restore em outro banco.
6. Coletar catálogo via psql do container e analisar offline. Exercitar constraints,
   planos, acesso de roles e locks em sessões próprias, sem carga de produção.
7. Parar serviços ao terminar. Preservar volumes/evidências; excluir só sob autorização.

Readme do boilerplate traz comandos reproduzíveis. O usuário administrador é para
operação do lab; aplicações precisam de role própria. Não trazer dumps reais sem
classificação, autorização e tratamento apropriado. Laboratório não entrega PITR/HA.
