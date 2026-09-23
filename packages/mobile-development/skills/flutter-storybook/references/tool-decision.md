# Decisão de ferramenta

## Widgetbook — padrão recomendado

Escolher quando o projeto quer um catálogo ativo de widgets e telas, use cases nomeados, addons, mocks e evolução para testes visuais. Verificar a versão compatível com o SDK fixado antes de adicionar.

## storybook_flutter — alternativa

Escolher quando já houver investimento no pacote, uma integração necessária com seus plugins ou um requisito explícito de manter a API Storybook. Validar a idade da versão, compatibilidade com Flutter/Dart, manutenção e suporte aos goldens desejados.

## Critério de reversibilidade

As stories devem depender de widgets e contratos do app, não de APIs específicas além de um pequeno adaptador. Assim, trocar a ferramenta muda a camada de catálogo, não o design system nem as páginas.
