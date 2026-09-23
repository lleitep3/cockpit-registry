---
name: mobile-developer
description: Planeja e implementa produtos mobile escolhendo Flutter, Android, iOS ou composição híbrida conforme requisitos de plataforma, acessibilidade, ciclo de vida, dados e release. Use em trabalho mobile; não use para uma crítica visual isolada.
---

# Desenvolvimento mobile

Escolha a menor arquitetura capaz de atender ao produto sem apagar diferenças reais entre Android, iOS e Flutter. Código compartilhado é uma ferramenta, não um objetivo que justifica degradar a experiência nativa.

## Antes de escolher tecnologia

Mapeie:

- plataformas, versões mínimas, form factors e distribuição;
- necessidade de UI idêntica ou comportamento nativo;
- offline, sincronização, notificações, deep links e background tasks;
- permissões, biometria, câmera, localização, Bluetooth e outros recursos nativos;
- acessibilidade, teclado, leitor de tela, escala de texto e internacionalização;
- tamanho da equipe, experiência, CI/CD, observabilidade e prazo de manutenção.

## Roteamento

- **Flutter**: quando compartilhamento de UI/lógica, velocidade e consistência visual pesam mais que integração profundamente nativa. Use `flutter-developer` e `flutter-storybook`.
- **Android nativo**: quando o produto depende fortemente de APIs Android, integração com serviços Google ou padrões Material/Jetpack específicos.
- **iOS nativo**: quando o produto depende de APIs Apple, SwiftUI/UIKit, widgets, Live Activities, watchOS ou comportamento iOS de primeira classe.
- **Híbrido**: quando a maior parte é compartilhável, mas capacidades críticas precisam de módulos nativos bem delimitados.

Não escolha por preferência pessoal antes de mapear os requisitos. Registre a decisão e o custo de reversão.

## Arquitetura

Organize por feature/capacidade. Separe apresentação, estado, domínio, dados e integração de plataforma. Em Flutter, a referência padrão é View/ViewModel + Repository/Service; em nativo, preserve equivalentes claros, como UI/state/domain/data/platform.

Bridges nativas devem ter contratos pequenos, erros explícitos, ciclo de vida documentado e testes no lado Dart/Swift/Kotlin quando aplicável. Não espalhe chamadas de platform channel pela UI.

## UI e design system

Defina tokens, estados, semântica e acessibilidade antes de telas. Em Flutter, use o catálogo visual do `flutter-development-kit`. Em nativo, mantenha componentes e tokens equivalentes sem fingir que Material e Human Interface Guidelines são a mesma coisa.

Cataloge loading, empty, error, sucesso, disabled, foco, texto longo, escala ampliada, offline e permissões. Páginas podem usar fakes determinísticos antes dos serviços reais.

## Qualidade mobile

- Teste cold start, background/foreground, rotação, restauração de estado e rede degradada.
- Verifique Safe Area, insets, teclado, gestos, leitores de tela e contraste.
- Faça testes unitários, UI/widget, integração, golden quando aplicável e smoke em builds de release.
- Meça performance em dispositivos representativos; não confie só em simulador.
- Não inclua segredos em configuração, logs ou artefatos de release.
- Trate assinatura, permissões e configuração por ambiente como contratos revisáveis.

Para critérios detalhados, leia [platform-decision.md](references/platform-decision.md) e [mobile-checklist.md](references/mobile-checklist.md).
