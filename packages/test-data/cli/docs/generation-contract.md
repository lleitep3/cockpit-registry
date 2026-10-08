# Receita executável v1 — Massa CLI 0.2.0

## Escopo aceito

Raiz obrigatória: `version: 1`, `seed` inteiro, `locale` Faker, `reference_time`
ISO-8601 com timezone e `entities`. Opções desconhecidas são recusadas pelo
contrato fechado. Usar strings entre aspas para timestamps YAML.
JSON Schema para suporte do editor: `examples/generation-contract.schema.json`,
gerado a partir de `Recipe.model_json_schema()`. Regerar ao alterar o contrato.

Cada entidade tem `count` inteiro não negativo, `fields` e, opcionalmente,
`references`. Limite inicial do motor em memória: 100.000 registros no total.
É uma proteção operacional desta versão, não alvo de desempenho validado.
Identificadores de entidade são ASCII, letras/dígitos/underscore, sem começar
por dígito. Selecionar um subconjunto das entidades do schema é permitido.

Cada campo do schema da entidade selecionada precisa estar em `fields` ou em
uma referência, exatamente uma vez. O motor ainda não omite campos calculados
ou com default automaticamente. Não carregar identity/generated em banco sem
uma estratégia apropriada: o CLI não oferece comando de carga nesta versão.

| Gerador | Opções | Resultado |
| --- | --- | --- |
| sequence | start inteiro, padrão 1 | Inteiro incrementado por linha |
| faker | provider | Provider sem argumentos |
| constant | value | String, inteiro, booleano ou null |
| template | value | String com tokens `{{ campo }}` da mesma linha |
| choice | weights | Chaves string com pesos inteiros positivos |
| reference_time | nenhuma | Timestamp fixo da receita |

Providers permitidos: `name`, `first_name`, `last_name`, `email`, `uuid4`, `city`.
A lista pequena evita providers dependentes do relógio atual ou formatos sem
contrato. Locale sem suporte é rejeitado. Templates não executam código; nomes
de campos ausentes, expressões e ciclos falham.

## Relações

Referências são declaradas na entidade filha:

```yaml
references:
  - entity: clientes
    fields:
      clinic_id: clinic_id
      cliente_id: id
```

O mapping é `campo local: campo remoto`. Um único pai é sorteado por referência;
todos os campos são copiados desse registro. Cada FK precisa estar coberta por
uma referência conjunta com os mesmos pares e tabela/schema de destino. Assim,
o tenant não é sorteado separadamente. Relações adicionais sem FK também podem
ser explícitas. FKs entre schemas, pais fora da receita, pais sem registros para
filhos não vazios e dependências cíclicas são recusados.

## Verificações e limites

Geração verifica nulabilidade, tipos SQL suportados, PKs/constraints UNIQUE e
FKs cobertas pelas referências. Unicidade usa até 100 tentativas por registro,
terminando com erro quando não encontra valor. UNIQUE convencional aceita
tuplas com NULL; `NULLS NOT DISTINCT` é recusado nesta versão.

Tipos aceitos: smallint/integer/bigint com limites, boolean, text,
character varying com comprimento, uuid e timestamp with time zone. Enum,
decimal/numeric, jsonb, arrays, domains e outros tipos falham explicitamente.
Collations especiais, índices únicos parciais/por expressão, SQL de checks e
triggers não são interpretados. Verificar a carga no banco antes de aprovar
integridade completa. O manifesto marca essas capacidades como não verificadas.

Não há sintaxe executável para cenários/overrides ou regras entre datas ainda.
Recipes de cenários devem ser arquivos separados com constantes explícitas nesta
fatia. O template genérico do pacote test-data é uma proposta mais ampla; usar
`examples/relational/generation.yaml` como referência funcional deste CLI.

## Reprodução e saída

Faker usa instância com seed própria; seleção de referências/choices usa PRNG
local separado, também com seed. Entidades prontas são ordenadas por nome, e
campos/templates têm ordem determinística para as mesmas entradas.

O manifesto registra hashes SHA-256 dos bytes exatos de entrada, versões de
Python/CLI/Faker/Pydantic/PyYAML, contagens e hashes JSONL. Sem paths de conexão
ou timestamp de execução variável. JSONL tem chaves ordenadas e newline final.
Reprodução byte a byte requer os mesmos bytes de entrada, código, Python e
dependências fixadas em `requirements.lock`; não prometer equivalência em outra
plataforma/runtime sem teste. Fixtures não garantem presença de toda categoria
apenas por pesos probabilísticos.
