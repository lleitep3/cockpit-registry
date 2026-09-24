---
name: aws-expert
description: Aplicar conhecimento de AWS em segurança, identidade, billing, custos e operação.
---

# AWS Expert

Use esta skill ao escolher, configurar ou revisar serviços AWS. Verifique a
documentação oficial e preços atuais quando a resposta depender de limites,
região, regras de billing, API, produto ou preço.

## Conta e acesso

- Confirmar account ID e região antes de alterações.
- Preferir IAM Identity Center, roles assumíveis e credenciais temporárias.
- Aplicar least privilege e separar administração, deploy e runtime.
- Não compartilhar root credentials, access keys ou segredos no chat/repositório.

## Custos

- Configurar budgets e alertas antes de workloads persistentes.
- Padronizar `Client`, `Project`, `Environment`, `CostCenter` e `ManagedBy`.
- Ativar cost allocation tags e considerar o atraso de processamento dos dados.
- Usar Cost Explorer, Cost Categories e account tags quando aplicável.
- Diferenciar estimativa, preço publicado, imposto, crédito e custo operacional.

## Segurança

- Bloquear acesso público por padrão.
- Habilitar criptografia e versionamento quando compatível com retenção e custo.
- Usar URLs temporárias para arquivos privados.
- Não colocar dados clínicos ou pessoais em tags, nomes de recursos ou logs.
- Definir backup, retenção, restauração e observabilidade antes de produção.

## Operação

- Tratar Organizations, contas, OUs e billing como fronteiras administrativas;
  tags e Cost Categories como classificação financeira, não como isolamento.
- Revisar dependências entre serviços e o impacto de migração para a conta do
  cliente.
- Verificar o estado real após o apply e registrar evidências.

## Comando de custos

Use o CLI do pacote para separar três perguntas:

- actual: quanto a AWS já processou no período, agrupado por serviço;
- forecast: qual a previsão estatística para o mês corrente;
- estimate: qual cenário resulta do estado Terraform e de premissas explícitas
  de uso.

Para os dois primeiros comandos, a identidade precisa de ce:GetCostAndUsage
e ce:GetCostForecast. Essas chamadas são somente leitura, podem ter custo por
requisição e os dados do mês corrente têm atraso. Nunca tratar estimate como
valor garantido da fatura.

Para uma conta compartilhada, use o filtro --cost-center partilhar. A tag precisa
estar ativada como cost allocation tag e pode levar até 24 horas para aparecer
nos dados de billing.
