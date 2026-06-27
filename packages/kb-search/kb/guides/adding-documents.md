---
title: "Adding Documents to the Knowledge Base"
description: "How to create and add documents to the AICockpit KB"
tags: ["kb", "documents", "add", "guide"]
author: "AICockpit Team"
version: "1.0"
related: ["kb-overview"]
---

# Adding Documents to the Knowledge Base

## Quick start

```bash
cockpit kb add /path/to/my-document.md
```

## Document format

Every KB document must have a **YAML front-matter header** delimited by `---`:

```markdown
---
title: "Document Title"
description: "One-line description for search ranking"
tags: ["tag1", "tag2", "tag3"]
author: "Your Name"
version: "1.0"
related: ["other-doc-id"]
---

# Document content starts here

Use standard Markdown for the body.
```

### Required fields

| Field | Description |
|---|---|
| `title` | Used in search ranking and display |
| `description` | Boosted in keyword search |
| `tags` | Primary search keywords |

### Optional fields

| Field | Description |
|---|---|
| `author` | Document author |
| `version` | Document version |
| `related` | IDs of related documents |

## Good document types to add

| Category | Examples |
|---|---|
| Architecture | System design, data flow, component responsibilities |
| Conventions | Naming rules, code style, patterns used |
| Processes | How to deploy, run tests, create a PR |
| Troubleshooting | Common errors and their solutions |
| References | API docs, config options, environment variables |

## Adding a project root

To make an entire directory searchable:

```bash
cockpit kb root add /path/to/your/docs/folder
cockpit kb rebuild-cache
```

## Tips for searchability

- Put important keywords in the `title` and `description`
- Use specific `tags` (e.g. `"go-testing"` rather than just `"testing"`)
- Keep documents focused on one topic
- Update the `version` field when making significant changes
