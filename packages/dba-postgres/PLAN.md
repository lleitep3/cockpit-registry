# DBA PostgreSQL 0.1.0 — plano de entrega

Objetivo: inspecionar PostgreSQL e produzir decisões rastreáveis de modelagem e
performance, sem executar mudanças no banco. Proprietário: pacote dba-postgres.

- Três skills: diagnóstico, modelagem e performance.
- Quatro workflows: baseline, revisão de modelo, investigação e mudança segura.
- Coletor SQL fixo, somente leitura; CLI Python 3.10+ e psql; perfis Cockpit explícitos.
- DER e relatório offline; nunca coletar linhas, consultas SQL de sessões ou senhas.
- KB versionada com fontes oficiais e lições generalizadas, sem dados de clientes.

Compatibilidade: Linux/Codex. Catálogos PostgreSQL 16–18 como alvo, somente versões
executadas são consideradas verificadas. Sem promessa de suporte Windows ou outros providers.
Dependências: Python stdlib para análise; psql e Cockpit com config exec para coleta.
Nenhuma dependência Python externa. Sem nova infraestrutura ou custo de serviço.

Riscos: metadados podem revelar domínio; estatísticas parciais ou resetadas podem
induzir recomendações erradas. Artefatos privados por padrão, sem query text,
limites de execução, sem SQL arbitrário e sem aplicação automática de recomendações.

Validação: fixtures de schema/estatísticas, erros, negação de perfil, dados malformados,
serialização segura, proteção contra sobrescrita e integração PostgreSQL local.
Separar teste simulado de vault de conexão real. Validar manifesto e registry.

Recuperação: coleta falha sem mudanças; novos arquivos somente, sem sobrescrever.
Instalação adiciona assets próprios. Desativação via cockpit pkg uninstall, executada
somente se solicitada; não desfazer outros pacotes nem apagar evidências automaticamente.
Publicação em PR próprio, sem merge automático. Nenhuma alteração no Partilhar.
