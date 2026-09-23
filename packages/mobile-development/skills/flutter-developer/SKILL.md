---
name: flutter-developer
description: Planeja, estrutura, implementa e revisa apps Flutter com arquitetura por feature, design system, acessibilidade, testes e catálogo visual. Use em trabalho de desenvolvimento Flutter; não use para crítica visual isolada sem mudança de código.
---

# Desenvolvimento Flutter

Construa Flutter como produto multiplataforma, não como uma coleção de telas. Preserve separação de responsabilidades, estados explícitos, APIs de componentes semânticas e verificabilidade desde a primeira feature.

## Antes de alterar código

- Leia as decisões e requisitos do projeto; trate `sources/` como referência somente leitura quando essa regra existir.
- Consulte a base de conhecimento do projeto antes de propor arquitetura ou biblioteca.
- Inspecione `pubspec.yaml`, versão do Flutter/Dart, análise estática, testes, CI, ambientes e convenções existentes.
- Reuse padrões existentes quando forem coerentes; registre divergências relevantes.
- Se o projeto ainda não existir, registre a decisão de boilerplate em vez de criar dependências por hábito.

## Arquitetura padrão

Use a orientação oficial como base: UI e dados separados, normalmente com View + ViewModel na UI e Repository + Service nos dados. Organize por feature. Adicione domínio/use cases apenas quando a complexidade justificá-lo.

- View: composição, layout, animação, semântica e roteamento local simples.
- ViewModel: estado de apresentação, comandos, transformação e coordenação de dados.
- Repository: fonte de verdade, cache, retry, erro e transformação para modelos do app.
- Service: API, plugin ou fonte externa sem estado de negócio.

Uma biblioteca de estado ou navegação é uma decisão do projeto, não uma regra desta skill. Escolha pela versão fixada, testabilidade, ergonomia da equipe e custo de manutenção.

## Design system e catálogo

Antes de construir páginas de produto, estabeleça os tokens mínimos e o tema. Componentes devem consumir `ColorScheme`, `TextTheme` e papéis semânticos; não espalhe cores e espaçamentos literais.

Use a skill `flutter-storybook` para catalogar componentes, templates e páginas. Se ela estiver disponível, crie os estados visuais antes de ligar serviços reais. Páginas dependentes de dados devem usar fakes determinísticos.

Atomic Design é um vocabulário de composição, não uma obrigação de classificar todos os widgets. Prefira responsabilidades claras e APIs estáveis a uma hierarquia artificial.

## Qualidade obrigatória

- Modele estados de carregamento, vazio, erro, sucesso, disabled e recuperação quando aplicável.
- Considere escala de texto, contraste, foco, teclado/mouse, leitor de tela, SafeArea e diferentes larguras.
- Evite side effects em `build`, rebuilds amplos e trabalho caro em cada frame.
- Use `const` quando possível, listas lazy para coleções grandes e profile mode para diagnosticar performance.
- Escreva testes junto da implementação: unidade para regras/ViewModels, widget para UI/interação, integração para fluxos críticos e golden para estados visuais estáveis.
- Rode format, analyze e testes antes de declarar conclusão. Se algo falhar, reporte causa e impacto; não oculte falhas.

## Entrega

Explique o que foi alterado, decisões de arquitetura, estados cobertos, testes executados e limitações. Não declare uma tela pronta apenas porque ela compila: indique se dados reais, navegação, acessibilidade e estados de erro foram verificados.

Para detalhes de seleção de stack e checklist, leia [architecture-and-stack.md](references/architecture-and-stack.md) e [review-checklist.md](references/review-checklist.md).
