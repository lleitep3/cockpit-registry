# Workflow: mudança segura

O CLI deste pacote não executa alterações. Este workflow orienta trabalho posterior
quando a sessão autorizar implementação/operação.

Antes: evidência, objetivo mensurável, ambiente/owner, escopo, SQL revisado, versão,
janela, backup/restauração comprovados conforme risco, lock_timeout/statement_timeout,
plano de rollback ou recuperação e impacto sobre réplicas/aplicação.

- Schema deve ter migration versionada e testes de upgrade em dados representativos.
- Índice concorrente tem restrições transacionais e pode deixar índice inválido;
  verificar resultado, não repetir cegamente. Consultar documentação da versão.
- VACUUM FULL, REINDEX, remoção de índice/tabela e retenção exigem avaliar locks,
  espaço temporário, perda de dados e autorização da ação; diagnóstico não autoriza isso.
- Nunca encerrar sessões, mudar parâmetros globais ou instalar extensões implicitamente.
- Após falha/timeout remoto, inspecionar estado antes de retry: resultado pode ser incerto.

Depois: validar invariantes, SLO, replicação, espaço/locks e dependências. Registrar
métrica anterior/posterior e janela. Salvar aprendizado comprovado na KB, não a senha
nem o dump. Plano de recuperação não é sinônimo de down migration.
