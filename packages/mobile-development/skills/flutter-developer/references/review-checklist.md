# Revisão Flutter

## Arquitetura

- [ ] Feature está isolada e tem fronteiras claras.
- [ ] View não conhece detalhes de API, banco ou plugin.
- [ ] Repository concentra fonte de verdade e política de dados.
- [ ] Side effects têm ciclo de vida explícito.
- [ ] Dependências podem ser substituídas nos testes.

## UI e design system

- [ ] Componente usa tokens e tema, não valores visuais espalhados.
- [ ] Estados relevantes estão nomeados e reproduzíveis.
- [ ] Layout funciona nos tamanhos suportados.
- [ ] Texto longo, escala ampliada, foco e contraste foram considerados.
- [ ] Semântica e navegação por teclado foram verificadas onde aplicável.

## Testes e performance

- [ ] Unidade para regras e ViewModels.
- [ ] Widget para interação e estados.
- [ ] Golden para visual estável.
- [ ] Integração para fluxo crítico.
- [ ] Analyze, format e testes executados.
- [ ] Não há trabalho caro em `build`, listas não-lazy desnecessárias ou rebuilds amplos.
