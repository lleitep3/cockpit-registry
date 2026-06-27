---
title: "AICockpit Knowledge Base — Overview"
description: "What the KB is, how it works, and why AI providers should search it"
tags: ["kb", "knowledge-base", "overview", "search"]
author: "AICockpit Team"
version: "1.0"
---

# AICockpit Knowledge Base — Overview

## What is the KB?

The AICockpit Knowledge Base (KB) is a local, searchable repository of
project-specific documentation. It stores guides, references, examples, and
troubleshooting documents that AI agents can query during a session.

Unlike general LLM knowledge, the KB contains **your project's specific**:
- Architecture decisions and rationale
- Coding standards and conventions
- Deployment and CI/CD processes
- Troubleshooting guides
- API patterns and examples

## How it works

```
Developer writes docs → cockpit kb add → indexed locally
                                           ↓
AI agent needs info → cockpit kb search → relevant docs returned
```

The KB uses a keyword + scoring algorithm (no external dependencies, no LLM
needed for search).

## Storage

- Default root: `~/.cockpit/kb/`
- Additional roots: configurable via `cockpit kb root add <path>`
- Index cache: `.index.json` (rebuilt automatically or via `cockpit kb rebuild-cache`)

## Key commands

```bash
cockpit kb search "<query>"          # Search documents
cockpit kb search "<query>" --limit 5 # Limit results
cockpit kb list                      # List all documents
cockpit kb add /path/to/doc.md       # Add a document
cockpit kb remove <id>               # Remove a document
cockpit kb root list                 # List configured roots
cockpit kb root add <path>           # Add a KB root
cockpit kb rebuild-cache             # Force index rebuild
```
