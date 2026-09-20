# Contrato de catálogo

## Metadados mínimos

```text
path: Components/Forms/TextField
name: Error / Long label
intent: mostrar validação e quebra de layout
component: AppTextField
state: error
theme: light | dark
viewport: compact | medium | expanded
text_scale: 1.0 | 1.3 | 2.0
data_source: deterministic fake
design_reference: opcional
```

## Taxonomia recomendada

```text
Foundations/
Components/
  Actions/
  Forms/
  Feedback/
  Navigation/
Patterns/
Templates/
Pages/
  FeatureName/
```

Use a taxonomia como navegação, não como contrato rígido de pasta do app. O código de produção deve continuar organizado por feature e responsabilidade.

## Matriz de estados

| Tipo | Casos esperados |
| --- | --- |
| Controle | default, focused, hovered, pressed, disabled, loading, error |
| Conteúdo | curto, longo, vazio, truncado, ausência de imagem |
| Coleção | loading, empty, erro, sucesso, refresh, paginação |
| Página | loading, empty, erro recuperável, sucesso, sem permissão |
| Plataforma | compact, expanded, touch, teclado/mouse |
| Acessibilidade | escala ampliada, alto contraste quando suportado, semântica |
