# Plano — CLI e boilerplate de repositório de infraestrutura

**Pacote:** `cloud-infrastructure`
**Versão alvo original:** `0.2.0`
**Data:** 2026-09-23

## Objetivo

Adicionar ao pacote um CLI capaz de orientar a criação ou reutilização de um
repositório de infraestrutura e gerar um boilerplate Terraform seguro, genérico
e evolutivo a partir do repositório `partilhar-aba-infra`.

## Decisão de fluxo

O agente deve perguntar primeiro se já existe um repositório de infraestrutura:

- se existir, receber o caminho e validar a estrutura sem sobrescrever arquivos;
- se não existir, propor a criação em um diretório informado pelo usuário;
- a criação deve exigir destino vazio ou confirmação explícita de sobrescrita;
- valores do projeto devem ser parametrizados, nunca copiados como identidade
  fixa do Partilhar ABA.

O CLI também deve expor uma listagem dos componentes genéricos disponíveis no
boilerplate.

## Contagem estimada de componentes lógicos

| Componente | Objetivo | Dependências | Critério de aceite |
| --- | --- | --- | --- |
| `repository-boilerplate` | Template Terraform genérico e catálogo de componentes | Repo `partilhar-aba-infra`, base Terraform atual | Gera estrutura sem nomes, IDs ou segredos específicos |
| `repository-scaffolder-cli` | Perguntar, validar repo existente e gerar boilerplate | `repository-boilerplate`, Bash | `init` e `components` funcionam em modo interativo e não destrutivo |
| `agent-integration` | Ensinar agentes e skills a usar o CLI e registrar estimativas | CLI e regras cloud | Skills descrevem o fluxo e o resultado esperado |

**Total estimado:** 3 componentes lógicos.

Recursos internos do boilerplate — budget, storage privado, identidade Cognito e
root module de ambiente — serão catalogados como componentes Terraform
reutilizáveis, não como componentes de entrega do pacote.

## Componentes Terraform genéricos da primeira versão

| Componente | Origem | Status no boilerplate |
| --- | --- | --- |
| `governance/budget` | Budget do sandbox atual | Incluído como referência parametrizada |
| `storage/private-s3` | Bucket privado do sandbox atual | Incluído com bloqueio público e criptografia |
| `identity/cognito` | Módulo Cognito do repo `partilhar-aba-infra` | Incluído como módulo reutilizável |
| `environment/dev` | Root module e estrutura de ambientes do repo atual | Incluído como exemplo mínimo |

Bootstrap de backend S3, OIDC de CI e produção ficam fora da primeira versão,
porque ainda exigem decisões próprias de conta, domínio, retenção e segurança.

## Ordem de implementação e commits

1. Implementar e validar `repository-boilerplate`.
2. Commit exclusivo do boilerplate.
3. Implementar e validar `repository-scaffolder-cli`.
4. Commit exclusivo do CLI.
5. Atualizar `cloud-architecture`, `cloud-engineering`, agentes e README para
   consumir o CLI.
6. Commit exclusivo da integração dos agentes.
7. Implementar e validar cost-observability.
8. Commit exclusivo do componente de custos.
9. Conectar custos ao CLI, README e skill AWS.
10. Commit exclusivo dos consumidores.
11. Rodar validação do pacote, testes e comparar a contagem estimada com a final.

## Não objetivos

- Publicar automaticamente um repositório Git remoto.
- Criar conta AWS, backend remoto ou recursos AWS durante o scaffold.
- Sobrescrever um repositório existente sem confirmação explícita.
- Copiar secrets, state, plans, IDs de conta ou valores específicos do projeto.

## Extensão — observabilidade de custos

O pacote também terá um comando de custos com três leituras diferentes:

- cost actual: custo já processado no Cost Explorer, agrupado por serviço;
- cost forecast: previsão oficial da AWS para o período mensal corrente;
- cost estimate: inventário do estado Terraform e, quando fornecidas
  premissas de consumo, estimativa de cenário.

O estado Terraform descreve recursos, mas não conhece uso, tráfego, requisições,
armazenamento efetivo ou usuários ativos. Por isso, a estimativa baseada apenas
no estado será apresentada como cenário incompleto, nunca como previsão de
fatura. A previsão de cobrança deve continuar vindo do Cost Explorer.

### Contagem revisada de componentes lógicos

| Componente | Objetivo | Dependências | Critério de aceite |
| --- | --- | --- | --- |
| repository-boilerplate | Template Terraform genérico | Terraform e módulos catalogados | Scaffold sem identidade do projeto original |
| repository-scaffolder-cli | Validar ou gerar repositórios | Bash e boilerplate | ,  e  testados |
| agent-integration | Aplicar a postura cloud | CLI, skills e regras | Fluxo de planejamento e commits documentado |
| cost-observability | Expor custo realizado, previsão e cenário | AWS CLI, Cost Explorer e Terraform state | Comandos separados, permissões mínimas e avisos sobre limitações |

**Total estimado revisado:** 4 componentes lógicos.

### Dependências e permissões do componente de custos

- AWS CLI autenticado na conta correta;
- ce:GetCostAndUsage para custo realizado;
- ce:GetCostForecast para previsão mensal;
- terraform show -json para inventário do estado local;
- pricing:GetProducts somente se uma etapa futura consultar preços
  publicados para recursos parametrizados.

As chamadas do Cost Explorer podem gerar custo por requisição e os dados de
billing têm atraso de processamento. O comando deve recomendar cache e deixar
claro o período consultado.

### Riscos, validação e rollback

- Risco: dados do mês corrente ainda não refletirem o consumo mais recente;
  validação: exibir período e timestamp da consulta.
- Risco: ausência de histórico suficiente para forecast;
  validação: tratar erro da AWS com mensagem orientativa.
- Risco: estimativa de estado ser confundida com fatura;
  validação: separar actual, forecast e estimate na saída.
- Rollback: remover o executável de custos e sua documentação; nenhuma chamada
  cria, altera ou destrói recursos AWS.


## Comparação final

| Medida | Planejado | Final | Desvio |
| --- | ---: | ---: | --- |
| Componentes lógicos do pacote | 4 | 4 | Nenhum desvio |
| Componentes Terraform catalogados | 4 | 4 | Nenhum desvio |
| Commits de entrega | 4 | 4 componentes | A documentação e os consumidores geraram commits adicionais; o componente de custos seguiu a separação prevista |
