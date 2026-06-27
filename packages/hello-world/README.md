# Hello World Package

A simple hello-world package for AICockpit that demonstrates how to create a basic package with a CLI command.

## Overview

This package adds a `hello` command to AICockpit that displays "hello world" when executed.

## Installation

```bash
cockpit pkg install hello-world
```

## Usage

```bash
cockpit hello
```

Output:
```
hello world
```

## Features

- Simple CLI command
- Works with all supported providers
- No external dependencies
- Fully documented

## Package Contents

```
hello-world/
├── cockpit-package.yml    # Package manifest
├── README.md              # This file
├── modules/
│   ├── cmd.go            # Hello command implementation
│   └── cmd_test.go       # Command tests
└── kb/
    └── guides/
        └── usage.md      # Usage guide
```

## Supported Providers

- ✅ Devin
- ✅ Goose
- ✅ Claude Code
- ✅ GitHub Copilot

## Requirements

- AICockpit >= 0.2.0

## License

MIT License

## Author

AICockpit Team

## Support

- Issues: https://github.com/lleite/cockpit-packages/issues
- Discussions: https://github.com/lleite/cockpit-packages/discussions
- Documentation: https://docs.aicockpit.dev/packages/hello-world
