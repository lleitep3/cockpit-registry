# Projeto de seed — plano de evolução após ambientes 0.4.0

Objetivo: IA prepara um projeto versionado, escolhe cenário, injeta dados no environment
explicitamente escolhido e verifica condições. Entrega: init/up/plan/apply/verify/status/reset.

Configuração YAML referencia arquivo de ambiente privado, banco esperado, tabelas
gerenciadas, migrations SQL e cenários. Cenário usa receita existente ou fixtures
explícitas ordenadas, com assertions estruturadas de contagem e filtros. SQL de
migrations e comandos up são código confiável do projeto, revisáveis; não são
inferidos da descrição em linguagem natural. IA traduz intenção em arquivos.

Proposta inicial de ownership para reset: vincular banco ao projeto em tabela
de controle, por migration explícita. Essa estratégia não foi implementada nem
restringe leitura/carga a bancos massa_*; conexão selecionada pelo usuário prevalece. Reset exige nome exato do
banco via --confirm; trunca somente tabelas declaradas, sem CASCADE. Aplicação,
assertions e recibo ficam na mesma transação. Falha reverte carga e reset combinado.
Advisory lock serializa comandos do projeto. Mesmo cenário/hash permite replay
somente após validar as assertions. Mudanças exigem reset ou replace explícito.

Comandos externos executam argv sem shell, sem despejar logs ou env. Configuração
do projeto é entrada confiável, não uma sandbox. Nunca usar o banco atual do
Partilhar sem escolha explícita: branch local está antiga. Usar migrations do ref
escolhido num banco dedicado. Nenhum seed Cognito implícito.

Testes: alvo remoto/banco divergente/unowned negados, path externo negado,
fixture desconhecida, assertions falsas, replay, concorrência via lock, rollback
transacional de replace, FK externa impedindo reset, saída sem credentials,
instalação do pacote e ciclo real Docker com cenários. Validação da aplicação
usa regras reais do ref, diferenciada de assertions de banco.

Sem reset de volume Docker ou importação de dados reais nesta
versão. Carga 0.5.0 aceita somente bundle gerado, manifestado e com escopo explícito. Depois: adaptadores de API, geradores adicionais e execução autenticada
para QA completo do ambiente.

Status: proposta, revisada após esclarecimento do usuário. Ambiente por referência
(.env/export Postman) e extração por tabela são o incremento atual. O destino de
carga/reset não foi escolhido; essas mutações não foram executadas. Mapear condições
de pendências e deep-links antes de transformar exemplos em cenários operacionais.

## Incremento 0.5.0

[seed plan/apply/verify](seed-project.md) implementados com manifesto, escopo por tabela, PKs, drift, plano confirmado, locks, transação e verificação dos valores fornecidos. Sem tabela de controle, reset/up/init ou assertions API/UI. Política de ownership e substituição acima permanece proposta para etapa futura; recibo em arquivo é pós-commit.
