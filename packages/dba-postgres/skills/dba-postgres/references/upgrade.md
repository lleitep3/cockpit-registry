# Workflow: upgrade e migração

1. Distinguir minor de major. Inventariar extensões, SO/arquitetura, encoding/collation,
   drivers, pooling, objetos especiais e dependências; ler notas das versões origem/destino.
2. Escolher estratégia conforme janela e volume: dump/restore, pg_upgrade ou replicação
   lógica têm requisitos e limites diferentes. Testar extensão e caminhos de upgrade.
3. Ensaiar em clone com dados representativos, validar compatibilidade, tempo e espaço.
   pg_upgrade --check é pré-checagem, não comprova sucesso funcional da aplicação.
4. Planejar freeze de escrita/cutover, backup recuperável, validação e ponto sem retorno.
   Depois de escritas no novo cluster, voltar ao antigo exige reconciliar dados;
   trocar endpoint não é rollback completo.
5. Após migrar: atualizar estatísticas conforme método, conferir sequências, grants,
   constraints, jobs, planos críticos, collation e réplicas; smoke da aplicação.
6. Não trocar major da imagem Docker sobre volume antigo. Preferir volume novo e
   migração explícita. Volume/banco antigo só é removido após autorização e retenção definida.

Saída: plano versionado, ensaio com métricas, checklist específico da versão e critérios
para seguir/reverter. Nenhum upgrade automático é realizado pelo pacote.
