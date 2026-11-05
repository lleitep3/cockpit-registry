# Operação e publicação

## Antes de mudar

Registrar equipe/ID, projeto/ID, ambiente, versão, domínio, proprietário e custo incremental. Confirmar escopo efetivo da credencial. Rever pacote web para que fontes, testes, instaladores, backups e segredos não sejam servidos. Configurar saída explícita em vercel.json e validar localmente. Seguir Git flow do repositório.

Preferir preview para avaliação; usar produção apenas se fizer parte do pedido. Controle de acesso e domínio estável têm efeitos em localStorage, cookies e links. Verificar proteção em cada URL, não só no endereço principal. Vercel Authentication e senha têm disponibilidades/custos distintos.

## Após publicar

Consultar deployment e status, obter URL real, verificar HTTPS, resposta, versão, navegação e persistência esperada. Confirmar custos/limites e dependências externas. Testes de desenvolvimento não comprovam prontidão para múltiplos clientes.

Rollback: escolher deployment conhecido e verificar domínio/versão após operação. Remover projeto, alterar DNS, revogar token ou trocar plano só com autorização correspondente. Timeout de POST/PATCH/DELETE: primeiro inspecionar estado e IDs; não repetir automaticamente.

## Respostas úteis

- 401: token inválido/expirado; renovar no perfil correto.
- 403: falta de escopo/permissão ou recurso indisponível no plano.
- 429: respeitar Retry-After e reduzir consultas.
- Rede/5xx em escrita: resultado desconhecido; reconciliar antes de repetir.
- CLI ausente: instalar versão fixa isolada e apontar VERCEL_CLI.
- Repo privado de organização: integração Git exige plano compatível; não tornar repo público para contornar.
