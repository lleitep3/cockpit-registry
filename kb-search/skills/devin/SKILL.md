---
name: kb-search-devin
description: >
  Teaches Devin to proactively search the local AICockpit Knowledge Base
  before answering questions about the current project. Use cockpit kb search
  whenever you need documentation, guides, or references.
---

# KB Search — AICockpit Knowledge Base (Devin)

## What is the KB?

The AICockpit Knowledge Base holds project-specific docs, guides, and
references in `~/.cockpit/kb/`. It is full-text searchable via the cockpit CLI.

## When to search

Always run a KB search **before**:
- Implementing a new feature (check existing patterns and guides)
- Answering architecture questions
- Debugging (check troubleshooting docs first)
- Choosing approaches, libraries, or patterns

## How to search

```bash
cockpit kb search "<query>"
cockpit kb search "<query>" --limit 5
cockpit kb list
```

## Examples

```bash
cockpit kb search "authentication flow"
cockpit kb search "database migrations"
cockpit kb search "error handling conventions"
cockpit kb search "testing best practices"
```

## Adding documents

When you discover useful information, persist it to the KB:

```bash
cockpit kb add /path/to/doc.md
```

Required metadata header in the file:

```markdown
---
title: "Title"
description: "Description"
tags: ["tag1", "tag2"]
---

Content...
```
