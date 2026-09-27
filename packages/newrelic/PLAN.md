# New Relic Cockpit package

Objetivo: configurar observabilidade reproduzível e investigar telemetria por API.
Proprietário: operador do Cockpit; conta/região/ambiente fornecidos por projeto.
Nenhuma aplicação cloud nesta entrega. Três componentes: CLI de leitura, template Terraform e duas skills.
Template: nove recursos New Relic, zero recursos AWS; aplicação exige conta, backend protegido,
plano Free/quota verificados e revisão do plano. Custos reais dependem do plano e ingestão.
Credenciais User via ambiente ou arquivo privado; nunca em argumentos, código ou state.
Validação: testes offline de autenticação, limites, erros e consultas; Terraform validate/test;
instalação local e smoke CLI. API real pendente de credencial válida e acesso autorizado.
Rollback: reverter instalação do pacote; template enabled=false desativa coleta e notificações.
Não remover state nem destruir recursos como rollback padrão.

| Medida | Planejado | Final | Desvio |
|---|---:|---:|---|
| Componentes do pacote | 3 | 3 | Nenhum |
| Recursos IaC no template | 9 | 9 | Nenhum |
| Recursos criados em contas cloud | 0 | 0 | Nenhum |

## Extensão 0.3.0
Componente adicional: bootstrap interativo de chaves. Planejado/final: 1/1.
Zero recursos Terraform adicionais; zero chaves reais criadas durante desenvolvimento.
Validação local: fixture Chrome/CDP, cofre simulado com PTY, erros e isolamento.
Criação real bloqueada até acesso administrativo permitido. Rollback: versão anterior
do pacote; nenhuma revogação automática de credenciais ou exclusão de perfil.
