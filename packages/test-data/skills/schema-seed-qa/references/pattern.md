# Padrão de schemas e seeds — versão 1

## Artefatos e responsabilidade

| Artefato | Origem | Regra de manutenção |
| --- | --- | --- |
| Migrations | Aplicação | Fonte da evolução física do banco |
| `schema.yaml` | Catálogo pós-migrations | Gerado; não receber regras manuais |
| `generation.yaml` | Time/projeto | Providers, dependências, cenários e invariantes |
| Manifesto da massa | Execução | Seed, versões, hashes, contagens e relógio |
| Relatório de QA | Verificação | Comandos, evidências, falhas e limites |

Versione contratos e pequenas fixtures sintéticas de referência. Massas grandes e
resultados temporários usam armazenamento/ignore do projeto. Não versionar secrets.
Schemas podem conter nomes internos e comentários: revisar antes de compartilhá-los.

## Preparação e extração

1. Identifique repositório, ambiente, banco, schemas e proprietário. Confira se a
   URL usada corresponde ao destino autorizado sem imprimir senha ou URL inteira.
2. Localize Compose/runbook e migrations antes de criar infraestrutura alternativa.
3. Suba banco local e execute migrations existentes quando autorizado. Seeds de
   autenticação ou serviços externos não fazem parte da extração estrutural.
4. Consulte catálogo em snapshot consistente, somente leitura e com timeout.
5. Preserve tipo SQL, ordem das colunas, nulabilidade, default, identity/generated,
   PKs, unicidade, FKs ordenadas, checks, índices e seus predicados.
6. Capture definições de triggers como evidência; registre dependências não
   exportadas, como funções, domains, RLS e partições. Não chamar isso de backup.
7. Exclua tabelas técnicas por política explícita. FKs para objetos excluídos ou
   outros schemas exigem resolução ou limitação documentada, nunca ID inventado.

## Evolução

Compare schema versionado e nova extração. Classifique inclusões, remoções,
alterações de tipo/default/nulabilidade e mudanças de chave/constraint/índice.
Renomeação exige mapeamento explícito, não inferência silenciosa.

Receitas que usam campo removido ou tipo incompatível devem falhar na validação.
Atualize schema e receita em mudanças revisáveis. O `diff/sync` automatizado só pode
ser usado quando implementado; antes disso, comparar arquivos e revisar manualmente.
Schemas seguem o banco pós-migrations do ref escolhido, não o nome da branch por si só.

## Receitas e coerência

`generation.yaml` deve declarar versão do contrato, seed, locale, relógio de
referência, entidades, contagens, campos, geradores e cenários identificados.
O exemplo em `../assets/generation.example.yaml` é contrato proposto, não executável
no extrator atual. A sintaxe final depende de validação e implementação do motor.

- FK composta é uma tupla selecionada do mesmo registro pai. `clinic_id` não pode
  ser sorteado independentemente dos demais componentes da FK.
- Gerar pais antes de filhos; ciclos precisam de estratégia explícita compatível
  com constraints, como inserção em fases ou constraints diferíveis. Nunca desativar
  constraints como solução automática.
- Campos generated/identity/default podem ser omitidos na carga para o banco
  calculá-los; exportação sem banco exige estratégia documentada.
- Valores monetários usam decimal/precisão definida, sem arredondamento implícito.
- Datas usam timezone definido, relógio fixo e relações temporais válidas.
- Unicidade deve detectar domínio insuficiente e terminar com erro claro, com
  tentativas limitadas. Não produzir loops infinitos ou remover constraints.
- Pesos descrevem distribuição, não garantem presença de cenários. Casos críticos
  precisam de fixtures/cenários explícitos com invariantes verificáveis.
- Dados inválidos pertencem a cenários negativos identificados. Separe validação
  prévia de payloads negativos e expectativas de rejeição pelo banco/API.
- Em ambiente multi-tenant, toda relação mantém isolamento do tenant.

## Reprodução e carga

Mesmo seed sozinho não garante igualdade. Fixar versão do gerador/providers,
receita, schema, locale, relógio, ordem e estratégia de aleatoriedade. Registrar
hash SHA-256 dos arquivos e contagens por entidade no manifesto. Não preencher
versões fictícias quando o motor não existir. Dependências devem ser fixadas/lockadas
antes de prometer reprodução em máquinas diferentes.

O manifesto não inclui paths privados, dados reais ou credenciais. Declarar quais
colunas serão produzidas pelo banco e qual equivalência está sendo verificada:
arquivo byte a byte ou conteúdo normalizado.

Carga em banco é etapa separada da geração. Confirmar destino local/teste e escopo;
usar transação quando compatível, registrar sucesso/falha e estratégia de repetição.
Rerun usa namespace/chaves controladas ou idempotência definida. Não truncar tabelas
para conseguir repetir. Rollback de transação não reverte efeitos externos nem
necessariamente sequências; registrar esses limites quando relevantes.
