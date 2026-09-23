---
title: "Desenvolvimento de backend com Clean Architecture"
description: "Orientação reutilizável para APIs modulares, interfaces explícitas e testes orientados por comportamento."
tags: ["backend", "api", "clean-architecture", "testing", "ports-and-adapters"]
author: "lleitep3"
version: "1.0"
---

# Desenvolvimento de backend

## Decisão padrão

Começar com um monólito modular e separar `domain`, `application`, `infrastructure` e `interfaces`. A tecnologia pode variar; a direção das dependências não.

## Plano mínimo de uma funcionalidade

1. entender o requisito e as invariantes;
2. escrever o plano de testes;
3. definir as portas;
4. testar o domínio;
5. testar o caso de uso com fakes;
6. implementar adaptadores;
7. expor e testar o endpoint;
8. executar integração e E2E quando a mudança cruzar fronteiras.

## Exemplo de primeira sequência

Identidade e autorização → pacientes → solicitações de edição → sessões → encaminhamentos → pendências → formulários → auditoria.

## Registro de decisões

Documente escolhas de linguagem, framework, banco, provedor de identidade, estratégia de auditoria e limites de escopo em ADRs do projeto. Uma skill fornece método reutilizável; não deve carregar regras clínicas específicas de um produto.
