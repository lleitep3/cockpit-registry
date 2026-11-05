# Estilo padrão de diagramas DBA

Use este estilo em todos os DERs e diagramas produzidos pelas skills do pacote,
salvo preferência explícita do usuário. Referência visual genérica, sem schema de cliente.

| Elemento | Cor |
| --- | --- |
| Fundo opaco | `#ffffff` |
| Texto, inclusive rótulos e atributos | `#111827` |
| Cabeçalhos | `#dbeafe` |
| Linhas alternadas | `#ffffff` e `#f1f5f9` |
| Bordas | `#475569` |
| Relações | `#334155` |

- Mermaid: copie [configuração](diagram-theme.json) na diretiva init do diagrama;
  use [exemplo genérico](diagram-example.mmd) como referência. O CLI já aplica o tema.
- Excalidraw, SVG ou HTML: reproduza a paleta, com fundo branco opaco, sem herdar
  cores do modo escuro. Não usar branco sobre linhas claras nem fundo transparente.
- Use fonte sem serifa, tamanho nominal 18px, zoom e rolagem em diagramas grandes.
  Ofereça visão resumida e detalhada quando ajustar tudo à tela tornar o texto pequeno.
- Preserve contraste mínimo de 4,5:1 para texto. Diferencie estados também por rótulo,
  nunca somente por cor. Preserve cardinalidades, tipos e legendas na exportação.
- Confira o artefato renderizado, incluindo rótulos de relações e todas as linhas
  alternadas. Alguns hosts ignoram tema Mermaid: nesse caso entregue SVG ou HTML
  com cores explícitas e fundo opaco, mais o fonte Mermaid editável.
- O exemplo autores/livros é fictício e serve apenas para estilo. Não copiar entidades
  do exemplo para análises reais nem incluir metadados de projetos neste pacote.
