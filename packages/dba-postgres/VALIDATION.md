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

## Versão 0.2.0 — 2026-09-28

- 19 testes do pacote passaram. Ruff e mypy --strict passaram para CLI e ensaio Compose.
- Docker Compose 2.27.0: config validado; PostgreSQL 17.11 com autenticação TCP
  correta aceita e senha errada recusada, persistência após restart, dump lógico
  restaurado em banco novo com dado sintético conferido e SQL operacional executado.
- pgAdmin 9.18: inicialização e página HTTP /login responderam 200. O teste não cobre
  login autenticado nem configuração de servidor na UI.
- Teste reproduzível: tests/lab_integration.py --output NOVA_PASTA --with-tools.
  Serviços parados ao final; volumes/evidências preservados. Nenhum banco de projeto alterado.
- O laboratório não implementa PITR, HA, backup externo ou configuração de produção.
  Estes temas têm workflows/KB, não automação homologada.
- Quatro skills, dez workflows e sete guias KB. Coletor remoto por perfil mantém
  os limites descritos na validação 0.1.0.

## Versão 0.2.1 — estilo de diagramas

- 20 testes passaram, incluindo tema embutido no Mermaid e exemplo genérico sincronizado.
- Paleta clara compartilhada pelas quatro skills; exemplo autores/livros sem schema de projeto.
- Validação de manifesto e registry executada. Nenhuma alteração de banco.
