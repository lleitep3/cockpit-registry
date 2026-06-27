---
title: "RTK Command Reference"
description: "Complete reference of rtk commands and their token savings"
tags: ["rtk", "commands", "reference"]
author: "AICockpit Team"
version: "1.0"
related: ["rtk-overview"]
---

# RTK Command Reference

## Go Development

| Command | Savings |
|---|---|
| `rtk go test ./...` | ~90% |
| `rtk go test -race -coverprofile=coverage.out ./...` | ~90% |
| `rtk go build ./...` | ~80% |
| `rtk go vet ./...` | ~80% |

## Git

| Command | Savings |
|---|---|
| `rtk git status` | ~70% |
| `rtk git add .` | ~59% |
| `rtk git commit -m "..."` | ~59% |
| `rtk git push origin <branch>` | ~59% |
| `rtk git log --oneline` | ~70% |
| `rtk git diff` | ~80% |
| `rtk git show` | ~80% |

## GitHub CLI

| Command | Savings |
|---|---|
| `rtk gh run list` | ~82% |
| `rtk gh run view <id> --log` | ~80% |
| `rtk gh pr view <num>` | ~87% |
| `rtk gh pr checks` | ~79% |
| `rtk gh issue list` | ~80% |

## File Operations

| Command | Savings |
|---|---|
| `rtk grep <pattern> <path>` | ~75% |
| `rtk find <path> ...` | ~70% |
| `rtk ls <path>` | ~65% |
| `rtk read <file>` | ~60% |

## Meta / Utility

```bash
rtk gain                # Show total token savings
rtk gain --history      # Per-command breakdown
rtk err <cmd>           # Show only errors from any command
rtk summary <cmd>       # Heuristic summary of any command
rtk proxy <cmd>         # Run without filtering (debugging)
```

## Command Chains

Always prefix **each** command in a chain:

```bash
# ✅ Correct
rtk git add -A && rtk git commit -m "feat: new feature" && rtk git push origin main

# ❌ Wrong
git add -A && git commit -m "feat: new feature" && git push origin main
```
