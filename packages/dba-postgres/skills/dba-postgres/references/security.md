# Workflow: segurança e governança

1. Mapear dados, ambientes, owners e clientes. Definir matriz de funções: owner sem
   login, migration, aplicação, leitura/monitoramento e administração emergencial.
2. Revisar grants herdados, PUBLIC, default privileges, schemas/search_path, funções
   SECURITY DEFINER e extensões. Não consultar/exportar hashes de senhas.
3. Verificar HBA efetivo, ordem das regras, método de autenticação e alcance de rede.
   TLS deve verificar identidade do servidor conforme ambiente. Não abrir trust
   remoto nem desabilitar validação de certificado para contornar acesso.
4. Revisar isolamento: FKs compostas, autorização e RLS têm responsabilidades diferentes.
   Testar como role da aplicação; owner/superuser/BYPASSRLS podem alterar o resultado.
5. Planejar rotação com consumidores, pool e fallback. Um arquivo secret alterado não
   rotaciona automaticamente credenciais já inicializadas no banco.
6. Mapear classificação/retencão, auditoria, backup criptografado e quem pode restaurar.
   Não inventar prazo legal ou garantir compliance por checklist técnico.
7. Validar acessos permitidos/negados e registrar evidência sanitizada. Mudanças de
   grants/HBA seguem safe-change.md; evitar perder o único acesso administrativo.

Saída: matriz de acesso, riscos comprovados, mudanças propostas, testes e owner.
