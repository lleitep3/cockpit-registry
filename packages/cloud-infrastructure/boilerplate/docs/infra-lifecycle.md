# Lifecycle de infraestrutura AWS com Terraform

Status: proposta inicial para revisão na issue #1.

Este documento define o fluxo mínimo para alterar, validar, promover, implantar e reverter infraestrutura. A regra central é: toda mudança nasce no Git, passa por revisão e chega à AWS por automação reproduzível.

## Decisões de base

- Terraform é a fonte declarativa da infraestrutura; mudanças manuais no console são exceção operacional e devem ser reconciliadas no código.
- Cada ambiente possui state remoto separado. O backend S3 deve ter versionamento habilitado, criptografia, controle de acesso restrito e locking por use_lockfile = true.
- Os ambientes iniciais são dev, staging e prod. Sempre que possível, cada ambiente deve usar uma conta AWS separada.
- O CI/CD usa GitHub Actions com OIDC para assumir roles AWS temporárias. Não guardar access keys de longa duração no repositório.
- main é protegida. Produção só recebe mudanças vindas de PR aprovado, workflow rastreável e aprovação do ambiente protegido.
- A unidade de promoção é o commit Git. Cada ambiente gera seu próprio plan contra seu próprio state, mas todos usam o mesmo commit aprovado.

## Estrutura proposta

~~~text
modules/                       # módulos reutilizáveis, versionados e documentados
environments/
  dev/                          # root module e valores do ambiente
  staging/
  prod/
.github/workflows/              # validate, plan, apply e rollback
docs/                           # decisões e runbooks
~~~

Cada diretório em environments/ é um root module independente. O state deve ter chaves distintas, por exemplo __PROJECT_NAME__/dev/__AWS_REGION__/core.tfstate; nunca compartilhar o mesmo state entre ambientes.

## Lifecycle de uma mudança

### 1. Propor

Abrir uma issue descrevendo objetivo, impacto esperado, ambientes afetados, dependências, risco de destruição e estratégia de rollback. Criar uma branch curta a partir de main.

### 2. Alterar e revisar

Implementar a mudança em uma branch. O PR deve explicar:

- o que muda e por quê;
- quais recursos serão criados, alterados ou destruídos;
- impacto em custo, segurança, disponibilidade e dados;
- como validar depois do apply;
- como voltar ao último estado conhecido como bom.

Mudanças pequenas e autocontidas reduzem o raio de impacto e tornam a recuperação mais rápida.

### 3. Validar automaticamente

O workflow do PR executa, no mínimo:

1. terraform fmt -check -recursive;
2. terraform init -backend=false e terraform validate;
3. lint de Terraform;
4. scan de segurança e secrets;
5. policy checks para regras que forem adotadas;
6. terraform plan para cada ambiente afetado.

O plan é uma prévia: não altera a AWS. O resultado deve aparecer no PR e o artefato deve ter acesso restrito e retenção curta, porque plans podem conter valores sensíveis.

### 4. Aprovar e aplicar em dev

Depois da revisão, o merge em main dispara o apply em dev. O workflow deve:

1. fazer checkout do commit exato;
2. autenticar na role AWS de dev via OIDC;
3. executar terraform init;
4. gerar terraform plan -out=tfplan;
5. aplicar exatamente o arquivo salvo com terraform apply tfplan;
6. executar smoke tests e checar métricas/alarmes;
7. registrar commit, ambiente, resultado e links dos artefatos.

O apply nunca deve refazer silenciosamente um plan diferente do que foi revisado.

### 5. Promover para staging e prod

A promoção seleciona um commit que passou em dev; não se copia código manualmente entre branches de ambiente. Para cada destino:

1. gerar um novo plan contra o state daquele ambiente;
2. revisar diferenças e pré-condições;
3. aplicar em staging automaticamente ou com aprovação leve;
4. executar testes de integração e observação por uma janela definida;
5. solicitar aprovação do ambiente prod;
6. aplicar em prod usando o plan aprovado;
7. validar saúde, disponibilidade, segurança e custos anômalos.

O workflow de produção deve exigir branch protegida, revisão por outra pessoa quando possível, ambiente GitHub protegido e role AWS exclusiva de produção.

## Critérios de validação

Antes do deploy: código formatado, providers e módulos versionados, validação sem erro, lint e segurança aprovados, plan revisado, mudança sem drift inesperado e rollback identificado.

Depois do deploy: terraform plan sem mudanças inesperadas, smoke tests funcionais, logs sem erro novo relevante, alarmes estáveis, conectividade e permissões verificadas. Se a mudança afetar dados, executar também uma checagem de compatibilidade e integridade.

Drift deve gerar alerta e ser tratado por PR. Não usar terraform apply para encobrir drift sem entender sua causa.

## Rollback sem dor

Rollback de Terraform não significa restaurar cegamente um arquivo de state. O caminho normal é reimplantar a última versão conhecida como boa:

1. interromper a promoção atual e preservar logs, plan e commit;
2. identificar o último commit/deploy saudável daquele ambiente;
3. verificar se a mudança é reversível e se houve migração de dados, alteração irreversível ou dependência externa;
4. gerar um novo plan contra o state atual, a partir da versão anterior;
5. revisar o plan e obter a aprovação exigida pelo ambiente;
6. aplicar o plan pela mesma pipeline normal;
7. repetir smoke tests e monitoramento;
8. abrir registro de incidente e decidir entre corrigir para frente ou repetir o rollback.

git revert pode ser o mecanismo para criar a correção no código, mas não deve ser executado às cegas: o state e a realidade da AWS podem ter mudado. Recursos substituídos, migrações de banco, mudanças de schema, dados já gravados e integrações externas podem não aceitar downgrade. Nesses casos, preferir uma mudança compatível para frente, isolamento de tráfego ou restauração específica de dados por runbook.

A restauração de uma versão anterior do state no S3 é medida de emergência, não rollback de rotina. Antes dela: bloquear novas execuções, salvar uma cópia do state atual, confirmar a versão correta e ter duas pessoas revisando a operação. Depois: reconciliar o state com a infraestrutura real e executar um plan controlado.

Toda mudança de produção deve declarar antes do deploy: sinais que acionam rollback, responsável, comando/workflow, janela de observação, dependências e critério de sucesso. Rollback deve ser ensaiado em staging para mudanças de alto risco.

## Regras operacionais

- Não executar apply manual em produção, exceto incidente documentado.
- Não commitar .tfstate, plans, credenciais ou secrets.
- Não desabilitar locking para “destravar” uma execução. Usar force-unlock somente para um lock próprio, com o ID correto e após confirmar que não há operação concorrente.
- Não usar -auto-approve fora de uma pipeline controlada.
- Separar mudanças de infraestrutura, aplicação e dados quando isso tornar o rollback mais seguro.
- Manter histórico dos deploys bem-sucedidos com commit, ambiente, operador/aprovador e resultado.
- Medir tempo de deploy, taxa de falha, tempo de recuperação e quantidade de mudanças manuais para melhorar o processo.

## Referências para aprofundamento

### Guias e documentação

- [Terraform: automated workflow](https://developer.hashicorp.com/terraform/tutorials/automation/automate-terraform) — init, plan salvo, revisão humana e apply.
- [Terraform: S3 backend](https://developer.hashicorp.com/terraform/language/backend/s3) — state remoto, versionamento e locking.
- [Terraform: modules](https://developer.hashicorp.com/terraform/language/modules) — organização e reutilização.
- [AWS Prescriptive Guidance: CI/CD](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-caf-platform-perspective/ci-cd.html) — tudo como código, automação, janelas e documentação.
- [AWS Well-Architected: plan for unsuccessful changes](https://docs.aws.amazon.com/wellarchitected/latest/framework/ops_mit_deploy_risks_plan_for_unsucessful_changes.html) — rollback/fix-forward documentado, testado e observável.
- [GitHub: environments and deployments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments) — aprovações e proteção de ambientes.
- [GitHub: OIDC with AWS](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws) — credenciais temporárias sem access keys persistentes.

### Pessoas e obras de referência

- Kief Morris — [Infrastructure as Code, 3rd edition](https://www.oreilly.com/library/view/infrastructure-as-code/9781098150341/), referência prática sobre padrões e evolução de IaC.
- Jez Humble e David Farley — [Continuous Delivery](https://continuousdelivery.com/), referência para pipelines, feedback e releases repetíveis.
- Amazon Builders’ Library — [Ensuring rollback safety during deployments](https://builder.aws.com/content/3F04j2yRAAMBuPSPs50xwXZqg01/ensuring-rollback-safety-during-deployments), com foco em compatibilidade durante avanço e rollback.

### Papers

- [A systematic mapping study of Infrastructure as Code research](https://arxiv.org/abs/1807.04872) — mapa de problemas e linhas de pesquisa em IaC.
- [Static Analysis of Infrastructure as Code: a Survey](https://arxiv.org/abs/2206.10344) — panorama de análise estática, defeitos e segurança.
- [Problems and Solutions of Continuous Deployment: A Systematic Review](https://arxiv.org/abs/1812.08939) — problemas organizacionais, de processo, ferramentas e infraestrutura em CD.

## Próximas decisões

1. Confirmar contas AWS e regiões por ambiente.
2. Criar o bootstrap do backend S3 e das roles OIDC fora do state de aplicação.
3. Escolher lint, scanner e policy engine iniciais.
4. Definir smoke tests, alarmes e janela de observação de produção.
5. Implementar os workflows e ensaiar rollback em staging.
