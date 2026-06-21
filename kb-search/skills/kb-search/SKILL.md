---
name: kb-search
description: >
  Teaches the AI to proactively search the local AICockpit Knowledge Base
  before answering questions about the current project. Use cockpit kb search
  whenever you need documentation, guides, references, or examples about this
  codebase.
---

# KB Search — AICockpit Knowledge Base (Antigravity)

## What is the KB?

The local Knowledge Base contains project-specific documentation, guides,
references, and best practices stored in `~/.cockpit/kb/` (and any configured
additional roots). It is indexed by AICockpit and searchable via CLI.

## When to search

Search the KB **proactively** before:
- Answering questions about project architecture, patterns, or conventions
- Starting implementation of a new feature (check if there are existing guides)
- Debugging an issue (check troubleshooting documents)
- Making decisions about libraries, tools, or approaches used in the project

## How to search

```bash
# Basic search
cockpit kb search "<query>"

# Limit results
cockpit kb search "<query>" --limit 5

# JSON output (for programmatic use)
cockpit kb search "<query>" --format json

# List all documents
cockpit kb list
```

## Search strategy

Use specific keywords from the task at hand:

| Task | Example query |
|---|---|
| Understanding the config system | `cockpit kb search "configuration yaml"` |
| Finding coding standards | `cockpit kb search "code style conventions"` |
| Checking how tests are written | `cockpit kb search "testing patterns coverage"` |
| Finding API patterns | `cockpit kb search "api design patterns"` |
| Troubleshooting CI failures | `cockpit kb search "ci cd pipeline lint"` |

## KB roots

The KB can have multiple roots. Check what's configured:

```bash
cockpit kb root list
```

## Adding documents

When you discover important knowledge during a session, add it to the KB:

```bash
cockpit kb add /path/to/document.md
```

Document format (requires metadata header):

```markdown
---
title: "Document Title"
description: "Brief description"
tags: ["tag1", "tag2"]
author: "Author"
version: "1.0"
---

# Content here
```
