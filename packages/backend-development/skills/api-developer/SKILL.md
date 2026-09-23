---
name: api-developer
description: Planeja, implementa e revisa APIs mantendo Clean Architecture, portas explícitas, autorização no backend e testes definidos antes do código. Use para trabalho de backend/API; não use para crítica isolada de UI ou apenas configuração de infraestrutura.
---

# API developer

Desenvolva APIs como monólitos modulares inicialmente, preservando separação entre domínio, aplicação, adaptadores e interfaces externas.

## Antes de codificar

1. Leia os requisitos e decisões de domínio existentes.
2. Liste casos de uso, invariantes, permissões e transições de estado.
3. Escreva um plano de testes com cenários permitidos, negados, bordas e auditoria.
4. Defina as portas/interfaces necessárias nas fronteiras reais.
5. Só então implemente os casos de uso e adaptadores.

## Camadas

- **Domain:** entidades, valores, invariantes e regras; não conhece framework, banco, HTTP ou provedor de identidade.
- **Application:** casos de uso, comandos, resultados e portas; orquestra o domínio.
- **Infrastructure:** banco, migrations, repositórios, Cognito, auditoria, filas e integrações externas.
- **Interfaces:** controllers, DTOs, validação, autenticação HTTP, serialização e mapeamento de erros.

As dependências apontam para dentro. Controllers não acessam banco diretamente. Não crie interfaces artificiais para cada classe; crie portas quando houver uma fronteira ou uma necessidade de substituição/teste.

## Testes

- Domínio: unitários, rápidos e sem infraestrutura.
- Aplicação: casos de uso com fakes/spies de repositório e auditoria.
- Infraestrutura: integração com banco e adaptadores reais em ambiente isolado.
- HTTP: contrato, validação, autenticação e autorização.
- E2E: fluxos completos e acessos negados relevantes.

Um endpoint novo precisa ter um caso de uso, testes e uma decisão clara de autorização. Testes devem verificar efeitos observáveis, não detalhes internos de implementação.

## Segurança e autorização

- O provedor de identidade autentica; a API autoriza por perfil, escopo, vínculo e regra de domínio.
- Nunca confie em papel ou escopo enviado pelo cliente.
- Audite alterações, consultas sensíveis e transições de estado definidas pelo produto.
- Diferencie autenticação, autorização, auditoria e regra de negócio.

## Entrega

Para cada fatia vertical, entregue contrato HTTP, caso de uso, portas, implementação, testes e documentação. Leia [clean-architecture.md](references/clean-architecture.md) quando precisar detalhar estrutura ou estratégia de testes.
