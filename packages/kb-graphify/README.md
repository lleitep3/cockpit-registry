# kb-graphify

Cockpit package that integrates the Knowledge Base with [Graphify](https://github.com/lleitep3/graphifyy) — a local LLM semantic-graph engine — enabling vector-based search and auto-indexing on top of AICockpit's KB.

## Purpose

By default, `cockpit kb search` uses BM25 (keyword matching). `kb-graphify` extends the search pipeline with semantic graph search powered by a locally running Graphify instance, delivering more relevant results without sending data to external APIs.

## Requirements

| Dependency | Minimum version |
|---|---|
| AICockpit (`cockpit`) | `0.1.0` |
| `uv` (Python package manager) | any recent |
| Python | `>=3.11` |

> Graphify is installed automatically as a post-install step via `uv tool install "graphifyy[all]"`.

## Installation

```bash
cockpit pkg install kb-graphify
```

The installer will:
1. Copy the package files to `~/.cockpit/packages/kb-graphify/`.
2. Run `uv tool install "graphifyy[all]" --force` to install the Python backend.

## Configuration

```bash
cockpit kb-graphify configure
```

Follow the prompts to set your Graphify API key (if using the cloud backend) or confirm the local model path.

## Validation

```bash
cockpit kb-graphify validate
```

Verifies that the Graphify binary is reachable and the configuration is complete.

## How it works

Once installed, `kb search` automatically tries the Graphify extension first:

1. `bin/kb-search` is called with the user query — it queries Graphify's semantic graph.
2. If Graphify is unavailable or returns an error, the CLI falls back to BM25.
3. `bin/kb-index` is called after adding a new KB root — it pushes documents into the Graphify graph for future semantic lookups.

Force BM25 explicitly with:

```bash
cockpit kb search --bm25 "my query"
```

## Package structure

```
kb-graphify/
├── bin/
│   ├── kb-graphify   # Main CLI entry point
│   ├── kb-index      # Index a KB root into Graphify
│   ├── kb-search     # Semantic search via Graphify
│   ├── configure     # Interactive configuration script
│   └── validate      # Validate configuration
├── cockpit-package.yml
└── README.md
```

## Supported providers

`antigravity`, `devin`, `goose`

## License

MIT

## Runtime isolado

A versão 0.1.2 instala Graphify 0.8.46 com `scripts/install.sh` em `.venv` dentro
do pacote. Requer `uv`. Usa cópias do interpretador e preserva a instalação global
existente. `kb-search` e `kb-index` usam exclusivamente esse runtime; ausência ou
falha da instalação retorna erro. Credenciais e provider continuam no vault.

Teste sem chamar LLM: `.venv/bin/graphify --help`. A versão direta está fixada;
dependências transitivas ainda são resolvidas pelo uv e não constituem lock completo.
