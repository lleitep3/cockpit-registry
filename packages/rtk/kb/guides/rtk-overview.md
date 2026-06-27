---
title: "RTK Overview"
description: "What RTK is, how it works, and why to use it with AICockpit"
tags: ["rtk", "token-optimization", "productivity", "cli"]
author: "AICockpit Team"
version: "1.0"
---

# RTK (Rust Token Killer) — Overview

## What is RTK?

RTK is a CLI proxy that sits between your shell and AI models. It intercepts
command output, filters noise, and compresses results — reducing the tokens
sent to the LLM by **60–99%** on common development operations.

## How it works

```
[your command] → rtk (filter/compress) → [compact output] → LLM
```

RTK has dedicated filters for: `go test`, `git`, `gh`, `grep`, `find`,
`docker`, `kubectl`, and many more. For commands it doesn't know, it passes
through unchanged — so it's **always safe to prefix with `rtk`**.

## Why this matters

Every terminal command output consumes tokens in the model's context window.
Unfiltered outputs from `go test ./...`, `gh run view --log`, or `git log`
can waste thousands of tokens on boilerplate, progress bars, and padding.

RTK strips all of that automatically.

## Installation

Installed automatically by `cockpit pkg install rtk`.

Binary location: `~/.local/bin/rtk`

## Quick start

```bash
# Instead of:
go test ./...

# Use:
rtk go test ./...

# Check your savings:
rtk gain
```
