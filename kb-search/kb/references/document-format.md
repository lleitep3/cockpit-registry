---
title: "KB Document Format Reference"
description: "Complete reference for the AICockpit KB document metadata format"
tags: ["kb", "format", "reference", "metadata", "yaml"]
author: "AICockpit Team"
version: "1.0"
related: ["adding-documents", "kb-overview"]
---

# KB Document Format Reference

## Full metadata schema

```yaml
---
title: "string — required"
description: "string — required"
tags:
  - "string"          # required, at least one
author: "string"      # optional
version: "string"     # optional (e.g. "1.0", "2024-06")
related:
  - "document-id"     # optional, IDs of related docs
---
```

## Search scoring

The search engine ranks results using this priority order:

| Match location | Score weight |
|---|---|
| Title exact match | Highest |
| Tag match | High |
| Description match | Medium |
| Body content match | Lower |

## Document ID

The document ID is derived from the filename (without `.md`) and its root path.
Example: file `~/.cockpit/kb/guides/go-testing.md` → ID `go-testing`.

## File locations

| Location | Type |
|---|---|
| `~/.cockpit/kb/` | Default KB root |
| Any path added via `cockpit kb root add` | Additional root |

## Index cache

The index is stored as `.index.json` in each KB root directory. It is
automatically rebuilt when documents are added or removed. Force a rebuild with:

```bash
cockpit kb rebuild-cache
```

## Supported content

The body supports standard **CommonMark Markdown**:
- Headings (`#`, `##`, `###`)
- Lists, tables, code blocks
- Links and images
- Bold, italic, inline code
