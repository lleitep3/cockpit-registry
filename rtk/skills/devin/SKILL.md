---
name: rtk-devin
description: >
  RTK (Rust Token Killer) usage rules for Devin. Always prefix terminal
  commands with rtk to reduce token consumption by 60–99%. RTK is a transparent
  proxy — safe to use for every command.
---

# RTK — Token-Optimized Commands (Devin)

## What is RTK?

RTK is a CLI proxy installed at `~/.local/bin/rtk`. It intercepts command
output and compresses it before sending to the model — reducing tokens by
60–99% on common operations.

## Golden Rule

**Always prefix commands with `rtk`.**

```bash
# ✅ Correct
rtk git status
rtk go test ./...
rtk gh run list

# ❌ Wrong
git status
go test ./...
gh run list
```

## Command Reference

```bash
# Tests
rtk go test ./...
rtk go test -race -coverprofile=coverage.out ./...

# Build
rtk go build ./...
rtk go vet ./...

# Git
rtk git status
rtk git add .
rtk git commit -m "..."
rtk git push origin <branch>
rtk git log --oneline
rtk git diff

# GitHub CLI
rtk gh run list
rtk gh run view <id>
rtk gh pr create ...
rtk gh pr view <num>

# File operations
rtk grep <pattern> <path>
rtk find <path> -name "*.go"
```

## Chains

```bash
rtk git add -A && rtk git commit -m "fix: message" && rtk git push origin main
```
