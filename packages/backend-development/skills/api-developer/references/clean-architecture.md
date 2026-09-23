# Referência: Clean Architecture para APIs

## Estrutura sugerida

```text
src/
├── domain/
├── application/
├── infrastructure/
└── interfaces/
```

Organize subpastas por capacidade de negócio, não por tecnologia global. Por exemplo, `patients`, `sessions`, `forms`, `pending-items` e `audit` podem aparecer nas camadas em que possuem responsabilidades.

## Portas comuns

- `PatientRepository`: persistência necessária ao caso de uso.
- `AuditWriter`: grava eventos sem expor o mecanismo de armazenamento.
- `PendingItemReader`: consulta operacional unificada.
- `IdentityClaimsReader`: fornece identidade já validada pela borda.

As interfaces pertencem à camada que precisa da capacidade. Implementações concretas ficam na infraestrutura.

## Sequência test-first

```text
plano de teste
  → contrato/interface
  → teste que falha
  → domínio/caso de uso
  → adaptador
  → endpoint
  → integração
```

Comece por uma fatia pequena, como criar paciente, para validar a arquitetura antes de multiplicar módulos.

## Anti-padrões

- entidade de domínio importando decorators do framework;
- controller contendo regra de autorização ou transação;
- caso de uso conhecendo SQL ou detalhes do Cognito;
- repository retornando modelos ORM diretamente ao domínio;
- teste que apenas verifica chamada de método sem comportamento observável;
- interface criada apenas para cumprir uma convenção, sem fronteira real.
