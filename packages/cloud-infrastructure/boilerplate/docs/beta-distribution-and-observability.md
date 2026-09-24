# Distribuição beta e observabilidade

**Status:** proposta para implementação  
**Escopo:** piloto controlado do app __PROJECT_DISPLAY_NAME__  
**Relacionamento:** complementa [Lifecycle de infraestrutura AWS com Terraform](./infra-lifecycle.md)

## Decisão

Usar **Firebase App Distribution** como canal privado de distribuição de builds de teste e combinar:

- **Firebase Crashlytics** para crashes, erros não fatais e contexto técnico;
- **Firebase Analytics** para eventos mínimos de uso necessários ao debug e à avaliação do piloto;
- **TestFlight** para a distribuição iOS quando houver testers externos;
- **Google Play Closed Testing** como etapa posterior para o piloto Android mais próximo da experiência de loja.

O Firebase será o ponto operacional comum para grupos de testers, convites, versões e feedback. A distribuição não será feita por links públicos de APK/IPA, anexos, WhatsApp, Google Drive ou serviços genéricos de hospedagem de arquivos.

Esta decisão trata distribuição e telemetria do app. O backend, a autorização de usuários e os dados da aplicação continuam sujeitos aos ambientes e controles definidos na infraestrutura AWS.

## Objetivos

O piloto deve permitir:

1. escolher exatamente quem pode instalar cada build;
2. adicionar ou remover testers sem redistribuir manualmente o arquivo;
3. identificar crashes por versão, dispositivo e sistema operacional;
4. acompanhar eventos mínimos de uso para reproduzir problemas;
5. promover a mesma versão testada para o canal de loja adequado;
6. manter o custo dos produtos Firebase sem custo dentro do plano Spark durante o piloto.

## Limites de custo

Firebase App Distribution, Crashlytics e Analytics possuem opções sem custo, sujeitas às quotas, limites e políticas atuais do Firebase. O uso de outros produtos, como banco, storage, funções ou autenticação por SMS, pode gerar custos separados.

A distribuição iOS para terceiros exige Apple Developer Program. A conta Apple gratuita atende ao desenvolvimento e ao teste no próprio dispositivo, mas não substitui a assinatura necessária para um piloto externo via TestFlight. A anuidade do Apple Developer Program deve ser tratada como custo de plataforma, fora do custo do Firebase.

O CI também deve ter seus limites de minutos e runners revisados antes de automatizar builds em escala.

## Canais por plataforma

### Android

**Canal inicial:** Firebase App Distribution.

- Grupos iniciais: `interno`, `piloto-clinica` e `administracao`.
- Convites por e-mail, sem link público.
- Build distribuída como APK assinada para instalação de teste.
- Upload automatizado pelo pipeline de CI quando possível.

**Canal de consolidação:** Google Play Closed Testing.

Usar este canal quando o app estiver estável o suficiente para testar instalação e atualização pela Play Store. A trilha da Play Store não substitui a autorização da aplicação; o acesso a pacientes, sessões e formulários continua sendo decidido pelo backend.

A trilha interna do Google Play pode ser usada antes do Closed Testing para validação técnica. Contas pessoais novas podem ter requisitos adicionais de teste antes da publicação em produção; isso deve ser conferido no Play Console da conta responsável.

### iOS

**Canal inicial:** Firebase App Distribution para QA controlado, desde que a build esteja corretamente assinada.

**Canal recomendado para testers externos:** TestFlight.

- Grupos separados para equipe técnica e piloto da clínica;
- primeiro build externo sujeito à revisão beta da Apple;
- builds do TestFlight disponíveis por uma janela limitada de 90 dias;
- distribuição exige Apple Developer Program.

O desenvolvimento compartilhado pode continuar em Linux. A assinatura e o empacotamento iOS devem ocorrer em macOS ou runner macOS de CI. Certificados, chaves privadas e tokens não podem ser armazenados no repositório.

## Ambientes

O piloto deve separar pelo menos:

- **Preview:** builds frequentes, dados sintéticos e testers internos;
- **Staging:** fluxo ponta a ponta com dados sintéticos e grupo piloto restrito;
- **Production:** somente após aceite do piloto e revisão de segurança, autorização, backup e recuperação.

Toda build deve carregar ou expor tecnicamente:

- ambiente;
- versão semântica;
- número do build;
- commit de origem;
- plataforma;
- configuração de API utilizada.

Uma build de teste não pode apontar acidentalmente para produção.

## Pipeline esperado

A implementação deve evoluir o lifecycle de infraestrutura existente para incluir artefatos móveis:

1. branch de feature gera a build de validação;
2. CI executa testes e verificações de segurança;
3. build Android é gerada em runner Linux;
4. build iOS é gerada em runner macOS;
5. artefatos são enviados ao Firebase App Distribution para os grupos autorizados;
6. testers recebem convite e reportam feedback pelo canal definido;
7. Crashlytics e Analytics são verificados por versão e ambiente;
8. após aceite, a mesma versão é promovida para Google Play Closed Testing ou TestFlight externo;
9. promoção e deploy ficam associados ao commit Git e ao workflow rastreável.

Credenciais de Firebase, Apple, Google Play e CI devem ser armazenadas como secrets ou credenciais federadas do ambiente. Nunca commitar arquivos de configuração com tokens, certificados ou chaves privadas.

## Observabilidade

### Crashlytics

Obrigatório nas builds `preview`, `beta` e `release`.

Registrar, sem dados clínicos:

- versão do app e número do build;
- ambiente;
- plataforma e versão do sistema;
- identificador técnico pseudonimizado do usuário de teste, quando necessário;
- estado do fluxo no momento do erro;
- identificadores técnicos de sessão e formulário, sem nome de paciente ou conteúdo de resposta.

Não registrar tokens, senhas, nomes de pacientes, prontuários, respostas clínicas, observações livres ou payloads completos de API.

### Analytics

Usar eventos pequenos e estáveis, com parâmetros controlados:

| Evento | Finalidade |
|---|---|
| `app_opened` | Verificar abertura e versão em circulação |
| `sign_in_succeeded` / `sign_in_failed` | Diagnosticar acesso |
| `session_opened` | Verificar entrada no fluxo principal |
| `form_started` | Medir início do preenchimento |
| `form_saved_draft` | Diagnosticar salvamento parcial |
| `form_submitted` | Verificar conclusão |
| `sync_failed` | Identificar falhas de conectividade ou API |
| `feedback_submitted` | Relacionar feedback com a build |

Os eventos não devem conter texto livre, dados de pacientes ou respostas clínicas. Analytics não substitui logs estruturados no backend.

## Segurança e governança

- Manter testers em grupos nomeados e revisados periodicamente.
- Remover acessos quando a pessoa deixar o piloto.
- Usar contas individuais; não compartilhar credenciais.
- Separar permissões de tester, terapeuta, supervisor e administração.
- Manter o ambiente de teste com dados sintéticos.
- Revisar privacidade, retenção, acesso, recuperação e resposta a incidentes antes de dados clínicos reais.
- Registrar no convite qual ambiente está sendo usado e como reportar problemas.
- Tratar o identificador de tester como dado técnico mínimo, pseudonimizado e com retenção definida.

## Fora do escopo

Não usar como canal principal:

- APK ou IPA público hospedado manualmente;
- envio de binários por mensagem ou e-mail;
- distribuição iOS Ad Hoc para o grupo piloto;
- Apple Developer Enterprise Program;
- marketplace próprio.

Ad Hoc pode ser reservado para testes técnicos de dispositivos conhecidos. Enterprise e distribuição privada empresarial só devem ser reconsiderados caso a clínica exija estratégia corporativa de MDM.

## Critérios de aceite

- [ ] Tester não convidado não consegue obter uma build de piloto pelo canal oficial.
- [ ] É possível adicionar e remover tester sem gerar manualmente um novo arquivo para todos.
- [ ] Cada build exibe versão, ambiente e commit de origem.
- [ ] Um crash de teste aparece no Crashlytics com plataforma, versão e build.
- [ ] Os eventos definidos aparecem no Analytics sem dados clínicos.
- [ ] Builds Android e iOS usam ambientes não produtivos durante o piloto.
- [ ] O pipeline não contém certificados, tokens ou credenciais em texto claro.
- [ ] A instalação e a atualização são documentadas em guia curto para testers.
- [ ] A promoção para os canais de loja fica associada ao commit e ao workflow.
- [ ] O piloto é executado primeiro com dados sintéticos.

## Próximos passos

1. Confirmar identificadores dos apps Android/iOS e o projeto Firebase da organização.
2. Definir os grupos de testers e os responsáveis por aprovar convites.
3. Configurar Crashlytics, Analytics e App Distribution.
4. Definir runners Linux e macOS do CI.
5. Implementar a matriz mínima de eventos e propriedades técnicas.
6. Documentar secrets e permissões por ambiente.
7. Executar piloto interno com dados sintéticos.
8. Promover Android para Closed Testing e iOS para TestFlight externo após o aceite.

## Referências

- [Firebase App Distribution](https://firebase.google.com/docs/app-distribution)
- [Firebase Pricing](https://firebase.google.com/pricing)
- [Firebase Crashlytics](https://firebase.google.com/docs/crashlytics/get-started)
- [Firebase Analytics](https://firebase.google.com/docs/analytics)
- [Apple TestFlight](https://developer.apple.com/testflight/)
- [Apple Developer Program](https://developer.apple.com/programs/)
- [Google Play: testes internos, fechados e abertos](https://support.google.com/googleplay/android-developer/answer/9845334)
