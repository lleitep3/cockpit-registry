---
title: "Hello World Package Usage"
description: "Guide for using the hello-world package"
tags: ["hello-world", "example", "simple"]
author: "AICockpit Team"
version: "1.0"
---

# Hello World Package

## Overview

The hello-world package is a simple example package that demonstrates how to create a basic AICockpit package with a CLI command.

## Installation

```bash
cockpit pkg install hello-world
```

## Usage

### Basic Usage

```bash
cockpit hello
```

Output:
```
hello world
```

## What's Included

This package includes:

- **CLI Module**: A simple `hello` command that displays "hello world"
- **Documentation**: This usage guide

## Features

- ✅ Simple hello-world command
- ✅ Works with all supported providers (Devin, Goose, Claude Code, GitHub Copilot)
- ✅ No dependencies
- ✅ Fully documented

## Examples

### Example 1: Run Hello Command

```bash
$ cockpit hello
hello world
```

### Example 2: Get Help

```bash
$ cockpit hello --help
Display hello world message

A simple hello-world command that displays a greeting message

Usage:
  hello [flags]

Flags:
  -h, --help   help for hello
```

## Uninstallation

```bash
cockpit pkg uninstall hello-world
```

## Support

For issues or questions, visit:
- Issues: https://github.com/lleite/cockpit-packages/issues
- Discussions: https://github.com/lleite/cockpit-packages/discussions

## License

MIT License - See LICENSE file for details
