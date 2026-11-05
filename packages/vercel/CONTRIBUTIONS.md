# Contribuindo com o pacote Vercel

Use branch e PR no cockpit-registry. Preserve perfis explícitos e o uso do vault do core; não adicione armazenamento alternativo de tokens.

Antes do PR, execute `bash tests/run_test.sh` e `cockpit cockpit-builder validate /caminho/vercel`. No registro, rode os validadores de pacotes e de PR. O índice e o manifesto devem usar a mesma versão.

Mantenha skill, help e comportamento consistentes. Documente evidência simulada separadamente de API real. Novos comandos precisam cobrir falhas de credencial, seleção de equipe e resultados desconhecidos de escrita. Não envie tokens, perfis locais, caches ou runtimes.
