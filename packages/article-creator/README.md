# article-creator

Cockpit package that compiles structured Markdown files into rich HTML articles.

## Purpose

`article-creator` provides an AI skill and a CLI command (`cockpit article`) that guides an AI agent to author didactic articles in Markdown — with sections, tables, diagrams, callouts, a glossary, and code examples — and then compiles them into a self-contained HTML course.

## Requirements

| Dependency | Minimum version |
|---|---|
| AICockpit (`cockpit`) | `0.1.0` |

## Installation

```bash
cockpit pkg install article-creator
```

## Usage

### CLI

```bash
# Compile a Markdown article into HTML
cockpit article compile path/to/article.md

# Show help
cockpit article --help
```

### AI Skill

After installation the skill `article-creator` is automatically deployed to your configured AI providers (Devin, Goose, Antigravity).

When you ask the agent to *"write an article about X"*, the skill instructs it to:

1. Structure the content in Markdown with standard sections (Introduction, Concepts, Examples, Glossary).
2. Save the file to the workspace.
3. Compile it to HTML via `cockpit article compile`.

## Package structure

```
article-creator/
├── bin/
│   └── article          # CLI entry point (compiled Go binary)
├── skills/
│   └── SKILL.md         # AI skill definition
├── cockpit-package.yml  # Package manifest
└── README.md
```

## Supported providers

`devin`, `goose`, `antigravity`

## License

MIT
