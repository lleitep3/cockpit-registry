---
name: kb-search-goose
description: >
  Teaches Goose to proactively search the local AICockpit Knowledge Base
  before answering questions about the current project. Use cockpit kb search
  whenever you need documentation, guides, or references about this codebase.
---

# KB Search — AICockpit Knowledge Base (Goose)

## What is the KB?

The AICockpit Knowledge Base stores project documentation, guides, and
references locally at `~/.cockpit/kb/`. It is indexed and searchable without
any external dependencies.

## When to search

Search the KB **proactively** before:
- Answering questions about the project
- Starting a new task (look for relevant guides)
- Debugging (check troubleshooting docs)
- Making architectural or tooling decisions

## How to search

```bash
# Search with keywords
cockpit kb search "<query>"

# Limit number of results
cockpit kb search "<query>" --limit 5

# List all KB documents
cockpit kb list

# List KB roots
cockpit kb root list
```

## Good search queries

```bash
cockpit kb search "project structure"
cockpit kb search "deployment process"
cockpit kb search "code review guidelines"
cockpit kb search "environment variables"
cockpit kb search "troubleshooting errors"
```

## Adding to the KB

Discovered something worth documenting? Add it:

```bash
cockpit kb add /path/to/document.md
```

Documents need a YAML front-matter header:

```markdown
---
title: "Title"
description: "What this document covers"
tags: ["relevant", "tags"]
author: "Author"
version: "1.0"
---

# Document content
```
