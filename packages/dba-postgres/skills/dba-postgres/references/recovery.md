# Workflow: backup, restauração e DR

1. Registrar RPO, RTO, tamanho, taxa de escrita, extensões, roles, tablespaces, versão,
   destino e isolamento. Distinguir erro humano, perda de host e perda de região.
2. Escolher estratégia: pg_dump é lógico por banco; roles/globais e configs são itens
   separados. Backup físico + sequência WAL suporta PITR, com ferramentas/topologia próprias.
3. Verificar sucesso, integridade do artefato, retenção, criptografia, controle de acesso
   e independência do destino. Não registrar senha nem dump em repositório de código.
4. Restaurar backup confiável em destino isolado NOVO; validar compatibilidade de versões,
   owners/grants, objetos, constraints, contagens/invariantes e consultas da aplicação.
5. Medir tempos e perda de dados usando marcadores conhecidos. Checksums ou listagem
   do dump não provam restore. Simular recuperação real conforme o objetivo.
6. PITR: confirmar cadeia completa, timeline e alvo antes de promover; falta de WAL
   quebra recuperabilidade. Replica não substitui backup contra erro lógico replicado.
7. Planejar cutover, validação, rollback/retorno e comunicação. Não restaurar sobre origem
   nem promover replica por autorização apenas de análise. Inspecionar estado após timeout.

Lab inclui exercício lógico; não habilita archive_mode nem PITR. Produção exige plano
versionado, teste e autorização do escopo. Registrar RPO/RTO medidos, não presumidos.
