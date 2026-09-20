# Desenvolvimento mobile com o AICockpit

## Decisão

`mobile-development` é um pacote coordenador. Ele não substitui as skills específicas de Flutter nem presume que todo produto deve ser cross-platform. A decisão deve partir de capacidades, UX, equipe, ciclo de vida, dados, distribuição e custo de manutenção.

## Composição

- `mobile-developer`: decisão de plataforma e coordenação da implementação.
- `flutter-developer` e `flutter-storybook`: skills Flutter incluídas no pacote para manter uma instalação única.
- Android/iOS nativos: extensões futuras devem entrar como skills ou dependências próprias, com contratos claros.

## Fluxo recomendado

1. Levantar plataformas, versões, capacidades e distribuição.
2. Escolher Flutter, nativo ou híbrido com decisão registrada.
3. Definir módulos/features e fronteiras de plataforma.
4. Criar tokens, componentes, estados e catálogo visual.
5. Implementar uma feature vertical com dados fake e depois integração real.
6. Verificar ciclo de vida, rede, acessibilidade e dispositivos representativos.
7. Rodar testes e smoke de release antes de declarar a feature pronta.

## Limitações

O pacote fornece orientação e contexto para agentes; não cria automaticamente um app, não escolhe bibliotecas sem verificar o SDK e não substitui validação em dispositivos reais.
