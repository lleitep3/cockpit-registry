---
name: flutter-storybook
description: Cria e mantém um catálogo Storybook-like de componentes, estados, templates e páginas Flutter antes ou junto do app. Use para Widgetbook, storybook_flutter, use cases, goldens e revisão visual; não use para implementar lógica de negócio sem catálogo.
---

# Catálogo visual Flutter

Construa uma superfície de desenvolvimento determinística onde designers, produto e engenharia possam inspecionar componentes e páginas sem autenticação, backend ou navegação acidental do app real.

## Ferramenta padrão

Use Widgetbook por padrão: ele está ativo, foi feito para catalogar widgets e telas, trabalha com use cases e possui integração com addons e testes. `storybook_flutter` continua sendo uma alternativa válida quando houver requisito explícito, mas sua maturidade/atualização deve ser verificada antes de adotá-la.

Não trate a escolha da ferramenta como parte da arquitetura de produção. O catálogo deve importar componentes do app, não duplicá-los.

## Fluxo

1. Inspecione versão do Flutter/Dart e dependências existentes.
2. Defina tema, tokens e wrapper do catálogo antes das histórias.
3. Crie entradas para foundations e componentes básicos.
4. Cubra estados e variações que mudam decisão visual ou comportamento.
5. Componha patterns, templates e páginas com conteúdo fake estável.
6. Adicione addons de tema, viewport, densidade e escala de texto conforme a ferramenta escolhida.
7. Gere goldens para estados estáveis e corrija divergências intencionais antes de atualizar imagens.
8. Execute o catálogo e testes em CI; nunca dependa de rede real, relógio local ou credenciais.

## Contrato de cada entrada

Cada story/use case deve declarar ou tornar evidente:

- nome semântico e caminho no catálogo;
- componente/página e intenção de uso;
- dados e parâmetros controláveis;
- estado visual e comportamento esperado;
- tema, viewport e escala relevantes;
- limites: texto longo, vazio, erro, loading, disabled, foco e interação;
- mock/fake usado, quando houver dependência externa;
- vínculo com design aprovado, quando existir.

## Cobertura mínima

Para cada componente, avaliar `default`, `hover`, `focus`, `pressed`, `disabled`, `loading`, `error`, `empty`, conteúdo longo e conteúdo ausente conforme aplicável. Para cada página, avaliar carregamento, vazio, erro recuperável, sucesso e permissão/role quando a regra existir.

Não gerar combinações cartesianas sem valor. Priorize estados que alteram layout, mensagem, ação ou risco de uso.

## Páginas antes do app

Catalogar páginas antes da integração é recomendado. Use duas formas:

- **Presentational page**: recebe estado e dados por parâmetros; simples de testar e compor.
- **Contained page**: conecta ViewModel/estado, mas injeta fake repository/service no catálogo.

O catálogo não deve virar um segundo app. Navegação entre páginas só é necessária quando ela ajuda a verificar um fluxo visual; o caso individual deve continuar acessível de forma isolada.

## Goldens e acessibilidade

- Fixe viewport, tema, fonte e dados no golden.
- Não aceite golden como prova de comportamento completo; combine-o com widget tests.
- Verifique overflow com escala de texto ampliada e larguras pequenas.
- Verifique labels, foco, ordem de leitura e estados sem depender de cor isolada.
- Atualize goldens somente após revisar a mudança visual.

Para o contrato detalhado, leia [catalog-schema.md](references/catalog-schema.md) e [tool-decision.md](references/tool-decision.md).
