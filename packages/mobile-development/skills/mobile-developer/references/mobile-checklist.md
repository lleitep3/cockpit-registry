# Checklist mobile

## Produto e plataforma

- [ ] Plataformas, versões mínimas e dispositivos foram definidos.
- [ ] Capacidades nativas e permissões estão mapeadas.
- [ ] Offline, rede degradada, background e restauração foram considerados.
- [ ] Deep links, notificações e distribuição têm contrato.

## Arquitetura

- [ ] Features têm fronteiras claras.
- [ ] UI não acessa serviços ou bridges diretamente.
- [ ] Estado de sessão, cache e persistência têm fonte de verdade.
- [ ] Contratos de integração têm erro e lifecycle explícitos.

## UI e acessibilidade

- [ ] Tokens e estados estão documentados.
- [ ] Loading, empty, erro, sucesso, disabled e offline foram cobertos.
- [ ] Safe Area, teclado, gestos, escala de texto e leitor de tela foram verificados.
- [ ] Flutter usa catálogo visual antes da integração, quando aplicável.

## Release

- [ ] Testes unitários, UI/widget, integração e smoke executados.
- [ ] Build debug/profile/release foi verificado na matriz mínima.
- [ ] Assinatura, permissões e ambientes não expõem segredos.
- [ ] Logs, crashes e métricas têm cobertura mínima.
