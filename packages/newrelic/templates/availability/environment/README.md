# New Relic: disponibilidade gerenciada por Terraform

Nove recursos: dois pings SIMPLE, política, duas condições de alerta, painel privado,
destino de email, canal e workflow. Sem ingestão de logs/APM, agentes, screenshots,
credenciais HTTP ou dados clínicos. Recursos AWS existentes não mudam.

## Pré-requisitos e aplicação

1. Concluir cadastro Free, verificar email e confirmar account ID/região US ou EU.
   A região New Relic não é sa-east-1. Confirmar quota/plano sem cartão ou upgrade.
2. Autorizar uma user API key dedicada no New Relic com permissões necessárias de
   Synthetics, Alerts, Dashboards e notificações. A chave de ingestão/license não
   serve para Terraform. Não criar chave via recurso Terraform: isso colocaria seu
   valor no state. Não enviar chaves pelo chat ou versioná-las.
3. Disponibilizar a chave como TF_VAR_newrelic_api_key no ambiente do executor, por cofre
   ou arquivo privado fora do repositório; evitar histórico de shell e logs. Não
   habilitar TF_LOG. A variável do provider é sensitive e ephemeral (Terraform 1.10+); não persiste em plano/state nem tem output.
4. Preencher cópias privadas dos exemplos. O email fica no state por ser configuração
   do destino; sensitive oculta saída, não cifra state. Proteger backend e permissões.
5. Backend S3 novo para esta raiz: dev/newrelic/terraform.tfstate. Usar bucket privado,
   versionado, dono verificado e allowed_account_ids da AWS. Não reutilizar state de
   outro ambiente ou confundir ID AWS com ID New Relic.
6. Confirmar que AWS_SA_EAST_1 está disponível nas localizações públicas do destino.
   Configurar endpoints públicos sem dados/segredos. Não desabilitar verify_ssl.
7. Somente após conferir Free, definir free_plan_confirmed=true. O plano bloqueia
   enquanto essa confirmação permanecer false.
8. Executar init com backend privado, validate e plan -out=newrelic.tfplan. Primeira
   aplicação: nove adições, zero mudanças/exclusões. Revisar antes de apply.
9. Conferir primeira execução dos dois monitores, eventos SyntheticCheck, painel,
   configuração de email/workflow e entrega de notificação de teste autorizada.
   Repetir plan e verificar ausência de diferenças. Plano mock não valida acesso,
   disponibilidade regional, licença ou entrega de email.

## Operação

Ping simples: cinco minutos, uma localização, fora da cota de testes sintéticos
cobrados conforme limites publicados. Falhas persistentes são avaliadas em janelas
de cinco minutos durante quinze minutos, com atraso de ingestão de dois minutos.
Ausência de sinal abre incidente após vinte minutos; requer ter recebido sinal ao
menos uma vez. Esses tempos são de configuração, não garantia de entrega.
/health só verifica resposta da API, não o banco ou um fluxo autenticado.

Painel mostra sucesso HTTP e duração. Workflow filtra exclusivamente a política
criada e respeita silenciamentos. Revisar uso mensal e custo antes de adicionar logs,
agentes ou monitores de navegador. Nunca usar sessão clínica real em testes sintéticos.

Rollback reversível: enabled=false desabilita monitores, condições e workflow,
preservando recursos e histórico. Para reativar, plan/apply revisado. Nenhum destroy
é necessário. A disponibilidade da aplicação não depende destes monitores.

## Limites de Terraform

Cadastro, confirmação de email, aceite e login são etapas do proprietário. Credenciais
não ficam em código/state. Agentes de host e APM precisam de automação de runtime
(Ansible), allowlist de dados e chave de ingestão; não usar provisioners com secrets.
Esses agentes não são instalados por esta raiz. Nova conta AWS exige bootstrap/state
próprios e configuração dos endpoints, mesmo que a conta New Relic permaneça a mesma.

Fonte: [provider New Relic](https://registry.terraform.io/providers/newrelic/newrelic/latest/docs)
e [limites sintéticos](https://docs.newrelic.com/docs/synthetics/synthetic-monitoring/getting-started/monitor-limits/).
