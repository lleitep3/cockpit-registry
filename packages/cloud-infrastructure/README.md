# Cloud Infrastructure

Pacote do AICockpit para arquitetura e engenharia cloud com entrega incremental,
controle de custos e rastreabilidade por componente.

## Conteúdo

- `skills/infrastructure-critic`: revisão crítica de PRs Terraform/IaC, integração, variáveis, outputs e gaps.
- `kb/guides/infrastructure-review.md`: critérios reutilizáveis de revisão de infraestrutura.
- `kb/guides/terraform-pr-review-checklist.md`: checklist de PR Terraform.
- `kb/guides/aws-static-frontend-hosting.md`: padrão AWS para frontend estático de baixo custo.


## Postura central

Todo trabalho de infraestrutura segue a sequência:

1. Planejar e estimar a quantidade de componentes lógicos.
2. Documentar o plano, suas premissas, custos, dependências e riscos.
3. Criar um componente por vez.
4. Validar o componente e revisar o plano aplicado.
5. Criar um commit exclusivo do componente.
6. Criar os códigos consumidores em uma mudança separada.
7. Criar outro commit exclusivo dos consumidores.
8. Comparar a quantidade estimada com a quantidade final e registrar desvios.

Quando o workspace não for um repositório Git, o agente deve informar a limitação
antes de continuar adicionando componentes que deveriam ser commitados.

## Componentes

Um componente é uma unidade lógica de entrega, como budget, storage, identidade,
rede, banco ou compute. Recursos internos do provedor são contados separadamente
apenas como detalhe de implementação.

## Segurança e custos

- Confirmar conta, organização, região e ambiente antes de aplicar.
- Preferir conta do cliente para ambientes do cliente.
- Criar budget e tags de custo antes de recursos persistentes.
- Usar least privilege, criptografia, bloqueios de acesso público e state protegido.
- Nunca versionar credenciais, tokens, state ou variáveis sensíveis.
- Tratar `apply`, migrações e destruições como ações que exigem plano revisado.

## CLI de custos

O pacote inclui leituras somente de consulta:

    cloud-infrastructure cost actual --days 30 --cost-center partilhar
    cloud-infrastructure cost forecast
    cloud-infrastructure cost estimate --state terraform-show.json

actual consulta o Cost Explorer e agrupa o custo processado por serviço.
forecast recupera a previsão mensal oficial da AWS. estimate inventaria o
estado Terraform e soma apenas as premissas mensais informadas com
--assumptions, por exemplo {"aws_s3_bucket.assets": 1.25}.

A previsão da AWS é a referência para a próxima cobrança. O estado Terraform
sozinho não conhece tráfego, requisições, armazenamento efetivo ou usuários
ativos e, portanto, não produz uma fatura exata.
