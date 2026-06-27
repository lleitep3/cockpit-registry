# KB Search Package for AICockpit

Deploys Knowledge Base search skills to all active AI providers (Antigravity,
Devin, Goose) so they automatically query the local KB before responding.

## What it does

1. **Deploys skills** to each detected AI provider:
   - **Antigravity** → `~/.gemini/config/skills/kb-search/SKILL.md`
   - **Goose** → `~/.config/goose/skills/kb-search/SKILL.md`
   - **Devin** → skill available via cockpit
2. **Adds KB docs** — overview, how-to guide, and format reference
3. **On uninstall** — cleans up deployed skills from all providers

## Installation

```bash
cockpit pkg install kb-search
```

## After installation

AI providers will automatically:
- Search the KB before answering questions about the project
- Suggest adding new knowledge when something important is discovered

### Search the KB manually

```bash
cockpit kb search "query"           # search by keywords
cockpit kb search "query" --limit 5 # limit results
cockpit kb list                     # list all documents
```

### Add project documentation

```bash
cockpit kb add /path/to/document.md
```

Documents require a YAML front-matter header:

```markdown
---
title: "Title"
description: "Description"
tags: ["tag1", "tag2"]
---

Content...
```

## Requirements

- AICockpit >= 0.3.0

## Supported Providers

| Provider | Skill Location |
|---|---|
| Antigravity | `~/.gemini/config/skills/kb-search/SKILL.md` |
| Goose | `~/.config/goose/skills/kb-search/SKILL.md` |
| Devin | Via cockpit skill system |
