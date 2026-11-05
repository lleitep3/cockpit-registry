# Contas e tokens

1. Criar primeiro token em [Account Tokens](https://vercel.com/account/tokens), com escopo mínimo compatível e expiração quando oferecida.
2. Salvar: `cockpit vercel auth ALIAS --scope TEAM_SLUG --token`. Campo oculto não recebe valor em argv. Entrada stdin é opção para secret manager.
3. Conferir `accounts --profile ALIAS` e `status --profile ALIAS`. Cadastro sem API válida não prova conexão.
4. CLI: credencial injetada somente no filho, com scope fixo. API: origem api.vercel.com, sem redirects.
5. Para renovar, repetir auth com novo token e verificar antes de revogar o antigo no painel. Não remover outros tokens sem escopo autorizado.

A CLI Vercel 62.0.0 aceita VERCEL_TOKEN no ambiente. A documentação diz que token-create exige token clássico com escopo de conta; OAuth, token limitado à equipe ou projeto podem ser recusados. O comando do pacote guarda bearerToken diretamente no vault. Falha após criação exige reconciliação no painel, pois a resposta sensível não é persistida em arquivo.

O core pode registrar argv. Por isso --token é um indicador de prompt, e não uma opção com valor. Metadados públicos usam `cockpit config --namespace vercel`; segredos nunca são resolvidos por accounts. Em bloqueio do keyring, manter erro e usar unlock oficial; não migrar para texto simples.

Fonte: [CLI tokens](https://vercel.com/docs/cli/tokens), [autenticação REST](https://vercel.com/docs/rest-api/reference/welcome#authentication).
