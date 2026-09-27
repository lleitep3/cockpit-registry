---
name: newrelic-builder
description: "Cria e evolui monitores, alertas, notificações e dashboards New Relic por Terraform. Use para configuração de observabilidade; para investigar dados existentes, use newrelic-analyzer."
---

# New Relic Builder

Inspecione IaC existente antes de gerar outra raiz: reutilize state e evite duplicar
recursos. Confirme conta New Relic, região de dados, ambiente, proprietário, backend,
plano/quota, endpoints e destinatários. Conta AWS do backend é diferente da conta NR.
Registre escopo, recursos, custos, validação e rollback. Respeite autorização já dada;
novas permissões, destinatários e cobranças não estão implícitos no template.

Para projeto novo, `cockpit newrelic scaffold ./observability` cria arquivos sem aplicar.
Template disponibiliza 9 recursos: 2 SIMPLE pings, política, 2 condições NRQL,
destino/canal de email, workflow e dashboard privado. Localização padrão AWS_SA_EAST_1;
verifique disponibilidade no destino. Testes mock não comprovam licença nem acesso real.
O template inicial suporta região US/EU; para JP verifique suporte do provider antes de ampliar.

Leia `environment/README.md` gerado antes de configurar. Preencha cópias privadas de
backend.hcl.example e terraform.tfvars.example; mantenha segredos fora desses arquivos.
User API key é sensitive/ephemeral (Terraform >=1.10), injetada em TF_VAR_newrelic_api_key
por cofre ou executor protegido. A CLI de leitura usa NEW_RELIC_API_KEY ou
NEW_RELIC_API_KEY_FILE (0600, proprietário atual); não imprima/envie valor ao chat.
Não use chave license para Terraform. Não crie chaves via recurso que persista valor no state.

Execute fmt, init com backend protegido/versionado, validate, test e plan salvo em
local privado. Revise add/change/destroy e conta antes de aplicar o plano autorizado.
Primeira instalação padrão deve ter 9 add, 0 change, 0 destroy; registre desvios.
Após apply confira duas execuções reais, consultas SyntheticCheck, dashboard, workflow,
entrega do email de teste autorizado e plan sem drift. `enabled=false` é rollback
reversível que mantém histórico. Não destrua state/recursos para corrigir drift.

Para observabilidade além de HTTP, planeje instrumentação APM e hosts no runtime
(Ansible/container/OpenTelemetry), licença de ingestão e allowlist de dados. Terraform
sozinho não instala agente nem produz telemetria. Não coletar dados clínicos, corpos,
authorization, cookies ou parâmetros sensíveis. Ajuste retenção/volume ao plano atual.
Templates podem ser estendidos por Terraform para SLOs, métricas e painéis específicos;
valide schema/documentação oficial em vez de presumir que o pacote cobre todo New Relic.

Fontes: [provider](https://registry.terraform.io/providers/newrelic/newrelic/latest/docs),
[NerdGraph](https://docs.newrelic.com/docs/apis/nerdgraph/get-started/introduction-new-relic-nerdgraph/).

## Perfis multi-conta

`cockpit newrelic profiles add partilhar-dev --account 8554578 --region US --vault-key newrelic-partilhar-dev`
registra somente metadados locais; não salva um token nem concede permissões New Relic.
Para guardar uma chave válida, rode em terminal privado:
`cockpit newrelic --profile partilhar-dev profiles auth` (entrada oculta pelo cofre).
Nunca use --value ou cole chave no chat. Cofre bloqueado deve ser desbloqueado pelo
proprietário; o pacote respeita o bloqueio, sem namespace alternativo ou fallback.

`cockpit newrelic profiles list` lista metadados, sem consultar segredos.
`cockpit newrelic --profile partilhar-dev account` verifica acesso real.
`cockpit newrelic --profile partilhar-dev synthetics` consulta o ambiente selecionado.
Crie outros perfis para outras contas/regiões. Cada referência de cofre pode ter uma
chave distinta; privilégios reais pertencem ao usuário New Relic, não ao nome do perfil.
Não existe perfil padrão implícito. Perfil não combina com --account/--region nem
variáveis NEW_RELIC_* legadas, evitando mistura involuntária de conta e chave.
Metadados ficam em ~/.cockpit/newrelic/profiles.json (0600); token no cofre Cockpit.
Perfis não alteram permissões. configure keys pode criar novas chaves com confirmação; não revoga chaves antigas.
Perfis são usados pela CLI de análise; Terraform continua usando suas variáveis
efêmeras e configuração de conta/região revisada, conforme o builder.

## Bootstrap guiado

Para configurar chaves use `cockpit newrelic configure keys --profile NAME --types user license --plan`
para mostrar escopo sem efeitos. A criação deve ser executada em terminal interativo,
sem --plan: o operador confirma a conta e autentica no Chrome dedicado. Dependência:
`cockpit newrelic configure browser`. A chave vai diretamente ao vault, nunca ao chat.
User dá acesso à API; license envia telemetria; browser é somente para o agente web.
Não usar esse fluxo para contornar política de navegador ou acesso negado. Não reexecutar
criação com journal pendente sem reconciliar o resultado; não reutilizar chave exposta.
Consulte README.md do pacote instalado para limitações e recuperação. A IA pode
preparar/verificar metadados e orientar o usuário; não automatize sua senha/MFA/CAPTCHA.
