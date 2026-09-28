# Contribuições ao DBA PostgreSQL

Uma alteração de pacote por PR, versão semântica coerente com o escopo e manifesto/index
alinhados. Não incluir mudanças de core ou outros pacotes nesta contribuição.

Rodar tests/run_test.sh, integração Docker quando SQL mudar, Ruff e mypy --strict.
Validar builder e registry. Distinguir testes simulados, conexão real e CI.
Novas heurísticas precisam explicitar limitações e cobrir falsos positivos relevantes.

Não adicionar coleta de registros/query text, SQL arbitrário, comandos mutantes ou
credenciais sem revisar contrato de segurança, documentação e autorização de uso.
KB deve ter fontes oficiais, versão/data de revisão e evidência. Não publicar dados
operacionais de clientes como fixture. Preservar plano de rollback e compatibilidade.
