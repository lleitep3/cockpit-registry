# AI-DLC docs project boilerplate

Este boilerplate adiciona validação mínima para repositórios que mantêm intenção,
requisitos, decisões, critérios de aceitação e evidências em Markdown.

Copie o conteúdo para a raiz de um novo projeto documental:

```bash
cp -r boilerplates/docs-project/.github .
cp -r boilerplates/docs-project/scripts .
```

O workflow valida documentos alterados no Pull Request e roda os testes do
validador. Ele usa somente a biblioteca padrão do Python.

Não coloque segredos ou dados privados no CI.
