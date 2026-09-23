# Arquitetura e seleção de stack Flutter

## Princípios

1. Separação de responsabilidades antes de abstrações.
2. Feature-first para reduzir colisão e facilitar ownership.
3. Fonte única de verdade para estado de dados.
4. UI declarativa derivada de estado imutável quando possível.
5. Dependências substituíveis em testes.
6. Bibliotecas escolhidas após fixar SDK e validar manutenção.

## Estrutura de referência

```text
lib/
  app/
    app.dart
    router.dart
    theme/
  core/
    errors/
    networking/
    platform/
  design_system/
    foundations/
    components/
    patterns/
  features/
    feature_name/
      data/
      presentation/
      domain/        # somente se necessário
      feature_name.dart
```

A estrutura é um ponto de partida. Não criar `core` como depósito de utilitários sem dono; cada abstração deve ter consumidor e contrato claros.

## Decisões a registrar

| Tema | Pergunta | Critério |
| --- | --- | --- |
| Estado | Qual estado é local, de feature ou global? | Escopo mínimo e testabilidade |
| Navegação | Há deep links, web ou rotas protegidas? | Declaratividade, restauração e URLs |
| Dados | Qual é a fonte de verdade? | Cache, offline, retry, invalidação |
| Modelos | Há ganho com code generation? | Contratos, imutabilidade e custo de build |
| UI | Quais estados e breakpoints importam? | Evidência do produto e risco de uso |
| Plataforma | Quais inputs e capacidades existem? | Touch, teclado, mouse, acessibilidade e plugins |

## Pacotes candidatos

Use somente depois de verificar versões e compatibilidade:

- `flutter_lints`: baseline de lints Flutter.
- `go_router`: candidato para rotas declarativas e deep links.
- Riverpod, Provider ou Bloc: alternativas de estado; escolher uma, não misturar por feature sem motivo.
- `freezed` + `json_serializable`: candidatos para modelos imutáveis e serialização.
- Widgetbook: catálogo visual recomendado nesta base.

Nenhum pacote candidato substitui testes, contratos ou uma arquitetura compreensível.
