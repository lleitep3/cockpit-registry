# Evidências de validação — 2026-09-28

- 16 testes unitários/comportamentais passaram: cardinalidade opcional/composta,
  MATCH FULL, índices parciais, índices inválidos, metadata malformada/truncada,
  dependência ausente, perfil negado sem fallback, segredo fora de argv/erros,
  arquivos privados, symlink e sobrescrita recusados.
- SQL executado em PostgreSQL 17.11 local: baseline de schema vazio e fixture isolada
  com três tabelas, FK composta e índice parcial. Container de fixture sem rede,
  descartado após o teste. Nenhum banco de aplicação foi alterado.
- Contrato SQL retorna arrays JSON reais. Relatório/DER offline gerados do snapshot.
- Ruff e mypy --strict verificam implementação. Manifesto validado pelo builder.

A integração usa psql dentro do Docker; psql não está instalado no host nesta máquina.
A seleção/injeção por perfil e falha de vault foram simuladas nos testes. Não há
perfil real de banco configurado nem validação end-to-end do vault nesta entrega.
PostgreSQL 16 e 18 são alvos de compatibilidade, ainda não executados neste pacote.
Não afirmar homologação em Windows/macOS ou performance sob carga.

Reproduzir: `tests/run_test.sh`; integração opcional `python3 tests/integration.py`
(requer Docker e imagem postgres:17-alpine). Lint/tipos são ferramentas de desenvolvimento,
instaladas em venv, não dependências do runtime.

- Instalação local: comando cockpit dba-postgres disponível; três skills distribuídas
  por cockpit deploy. Manifesto restringe suporte declarado a Codex.
- Registry completo validado; 19 testes existentes do validador passaram.
- Quatro guias copiados como assets canônicos da KB e recuperados por
  `cockpit kb search dba-postgres --bm25`. kb add é stub nesta instalação.
  Graphify falhou por modelo configurado indisponível; busca semântica não validada.
