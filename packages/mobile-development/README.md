# Mobile Development

Pacote coordenador do AICockpit para desenvolvimento mobile cross-platform e nativo.

## Conteúdo

- `skills/mobile-developer`: escolha de plataforma, arquitetura, integração nativa, qualidade e release.
- `skills/flutter-developer`: arquitetura e implementação Flutter.
- `skills/flutter-storybook`: catálogo visual Flutter.
- `agents/mobile-developer.md`: perfil reutilizável para tarefas mobile.
- `kb/guides/mobile-development.md`: decisões, fluxo e checklist.
- `kb/guides/package-maintenance.md`: manutenção e versionamento do pacote.

O pacote é autossuficiente. Android/iOS nativos são tratados como extensões de plataforma quando o produto exigir; não há uma escolha automática de framework sem evidência de requisitos.

## Instalação normal

Depois de publicado e indexado em uma registry, use o package manager. Ele valida o manifesto e instala agentes, skills e KB nos destinos canônicos:

```bash
cockpit pkg install mobile-development
cockpit deploy
```

Não copie skills ou agentes manualmente para os diretórios canônicos.

## Staging local para desenvolvimento do pacote

O staging local é apenas para desenvolver e validar o pacote antes da publicação:

```bash
cp -R packages/mobile-development ~/.cockpit/local-registry/
cp -R ~/.cockpit/local-registry/mobile-development ~/.cockpit/packages/
```

Esse staging não substitui a instalação normal e não deve ser apresentado como pacote instalado pelo package manager. Publique somente este pacote.
