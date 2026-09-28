# Instalação e manutenção local

Origem editável: `~/.cockpit/local-registry/dba-postgres`.
Runtime: `~/.cockpit/packages/dba-postgres`.
Skills canônicas: `~/.cockpit/skills/{dba-postgres,postgres-modeling,postgres-performance,postgres-operations}`.

Usar mecanismo de instalação do Cockpit quando disponível no registry. Para staging,
validar/testar primeiro; copiar pacote sem caches para runtime e copiar somente as quatro
skills declaradas para skills canônicas. Preservar arquivos de outros pacotes.
Executar `cockpit deploy` para distribuir, nunca editar provider-generated SKILL.md.

Guias KB são declarados no manifesto. Para curadoria manual, pesquisar duplicatas,
importar cada guia com `cockpit kb add` usando contexto dba-postgres conforme a versão
instalada, e verificar recuperação. Se a ferramenta não oferece contexto, registrar
isso na evidência e manter a fonte versionada; não fingir importação contextual.

Desinstalação, quando solicitada: `cockpit pkg uninstall dba-postgres`, verificando os
assets geridos pela versão do core. Não apagar evidências nem outros pacotes.

## Limitação verificada do core instalado

Em 2026-09-28, `cockpit kb add` respondeu "Feature coming soon" e não persistiu
conteúdo; `--context` não é suportado. Guias permanecem versionados no pacote e
instalados como assets KB; não afirmar importação pelo comando nem busca contextual.

Nesta entrega, os sete guias foram copiados para `~/.cockpit/kb/guides/dba-postgres/`,
indexados e recuperados via `cockpit kb search dba-postgres --bm25`. Graphify falhou
por modelo indisponível; isso não impede leitura dos arquivos nem busca local BM25.

Para atualizar somente o índice local, usar `cockpit kb rebuild-cache --extensions=false`,
e confirmar com `cockpit kb search dba-postgres --bm25`. Isso evita depender da extensão
semântica e não altera sua configuração.
