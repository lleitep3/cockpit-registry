# Manutenção do pacote mobile-development

## Fonte versionada

A fonte de verdade é `packages/mobile-development/` no projeto. O staging local fica em `~/.cockpit/local-registry/mobile-development/`; a cópia de teste fica em `~/.cockpit/packages/mobile-development/`.

## Fluxo

1. Editar a fonte versionada.
2. Atualizar `CHANGELOG.md` e semver quando houver mudança distribuível.
3. Validar skills com `quick_validate.py`.
4. Copiar para `~/.cockpit/local-registry/mobile-development/` apenas como staging local.
5. Rodar `cockpit-builder validate ~/.cockpit/local-registry/mobile-development`.
6. Publicar/indexar somente este pacote.
7. Instalar com `cockpit pkg install mobile-development`; o package manager deve distribuir todos os assets.
8. Executar `cockpit deploy` após a instalação.
9. Atualizar entradas KB existentes pelo ID; não criar duplicatas.

Não copiar manualmente skills, agentes ou KB para os diretórios canônicos como substituto da instalação. A cópia para `~/.cockpit/packages/` é somente um procedimento de teste local documentado pelo AICockpit.

## Limite de responsabilidade

O pacote coordena mobile e contém as skills Flutter. Conteúdo nativo futuro deve ter skill própria quando houver requisitos suficientes.
