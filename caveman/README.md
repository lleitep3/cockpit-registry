# Caveman Package for AICockpit

Deploys the [caveman](https://github.com/JuliusBrussee/caveman) skill to all active AI providers — cuts **~75% of output tokens** while keeping full technical accuracy.

## What it does

Installs a skill that instructs the AI to respond in ultra-compressed "caveman speak":

**Normal (~70 tokens):**
> "The reason your React component is re-rendering is likely because you're creating a new object reference on each render cycle. When you pass an inline object as a prop, React's shallow comparison sees it as a different object every time..."

**Caveman (~19 tokens):**
> "New object ref each render. Inline object prop = new ref = re-render. Wrap in `useMemo`."

**Same fix. ~75% less words. Brain still big.**

## Installation

```bash
cockpit pkg install caveman
```

## Activation

```
/caveman          → full mode (default)
/caveman lite     → lite mode (no filler, keeps sentences)
/caveman ultra    → ultra mode (max compression)
```

Deactivate: `"normal mode"` or `"stop caveman"`

## Commands included

| Command | What it does |
|---|---|
| `/caveman [lite\|full\|ultra]` | Set compression level |
| `/caveman-commit` | Conventional Commit messages, ≤50 char subject |
| `/caveman-review` | One-line PR comments with severity |

## PT-BR support

Works natively in Portuguese — compresses the style, not the language.

> "Novo ref de objeto cada render. Prop inline = novo ref = re-render. Envolva com `useMemo`."

## Complementary with RTK

| Tool | Reduces |
|---|---|
| `rtk` | **Input** tokens (command output filtering) |
| `caveman` | **Output** tokens (response style) |

Install both for maximum token savings:

```bash
cockpit pkg install rtk
cockpit pkg install caveman
```

## Supported Providers

| Provider | Skill Location |
|---|---|
| Antigravity | `~/.gemini/config/skills/caveman/SKILL.md` |
| Goose | `~/.config/goose/skills/caveman/SKILL.md` |
| Devin | Via cockpit skill system |

## Credit

Based on [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) — MIT License.
