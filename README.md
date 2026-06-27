# AICockpit Official Package Registry

This is the official package registry for AICockpit. It contains packages that extend AICockpit functionality with new commands, skills, agents, and knowledge base documents.

## Overview

The AICockpit Package Registry is a Git-based repository that hosts packages for the AICockpit system. Each package can contain:

- **CLI Modules**: Custom commands that extend the `cockpit` CLI
- **Agents**: Autonomous AI agents for task execution
- **Skills**: Reusable capabilities that agents can leverage
- **Hooks**: Event handlers for system lifecycle
- **Workflows**: Automated workflows and automation patterns
- **Memories**: Memory and context management
- **Knowledge Base**: Documentation and learning materials

## Available Packages

### hello-world (1.0.0)

A simple hello-world package that demonstrates how to create a basic AICockpit package with a CLI command.

**Features:**
- Simple `hello` command that displays "hello world"
- Works with all supported providers
- No external dependencies
- Fully documented and tested

**Installation:**
```bash
cockpit pkg install hello-world
```

**Usage:**
```bash
cockpit hello
```

**Output:**
```
hello world
```

**Supported Providers:**
- Devin
- Goose
- Claude Code
- GitHub Copilot

**Status:** Stable

**Version:** 1.0.0

**Author:** AICockpit Team

**License:** MIT

## Package Registry Structure

```
cockpit-registry/
├── package-index.yaml          # Registry index (lists all packages)
├── README.md                   # This file
├── LICENSE                     # License file
├── .github/                    # GitHub workflows
│   └── workflows/
│       └── validate-packages.yml
├── packages/                   # Package directory root
│   ├── hello-world/            # Package directory
│   │   ├── cockpit-package.yml # Package manifest
│   │   ├── README.md           # Package documentation
│   │   ├── LICENSE             # Package license
│   │   ├── modules/            # CLI modules
│   │   │   ├── cmd.go
│   │   │   └── cmd_test.go
│   │   └── kb/                 # Knowledge base
│   │       └── guides/
│   │           └── usage.md
│   └── [other-packages]/       # Additional packages
│       └── ...
└── docs/                       # Optional registry documentation
    └── ...
```

## Package Index

The `package-index.yaml` file is the registry index that lists all available packages. It contains metadata about each package including:

- Name and version
- Description and author
- Supported providers and features
- Requirements and dependencies
- Installation method
- Status and release date

## Installation

### Default Registry Configuration

AICockpit is configured with this registry by default:

```yaml
package_registries:
  - name: "official"
    url: "https://github.com/lleite/cockpit-registry"
    branch: "main"
    enabled: true
    priority: 1
```

### Search Packages

```bash
# Search in all registries
cockpit pkg search hello

# Search in official registry
cockpit pkg search hello --source official

# List all packages
cockpit pkg list

# Search by category
cockpit pkg search --category examples

# Search by tag
cockpit pkg search --tag example
```

### Install Package

```bash
# Install package from default registry
cockpit pkg install hello-world

# Install specific version
cockpit pkg install hello-world@1.0.0

# Install from specific registry
cockpit pkg install hello-world --source official

# Install with dependencies
cockpit pkg install hello-world --with-dependencies
```

### Uninstall Package

```bash
# Uninstall package
cockpit pkg uninstall hello-world

# Force uninstall
cockpit pkg uninstall hello-world --force
```

## Creating a Package

To create a new package for this registry:

### 1. Create Package Directory

```bash
mkdir -p packages/my-package/{modules,skills,agents,kb}
```

### 2. Create Package Manifest

Create `packages/my-package/cockpit-package.yml`:

```yaml
name: "my-package"
version: "1.0.0"
description: "My awesome package"
author: "Your Name"
license: "MIT"

type: "utility"
category: "utilities"

requirements:
  cockpit: ">=0.2.0"

features:
  modules:
    - path: "modules/cmd.go"
      name: "my-command"
      description: "My custom command"

installation:
  supported_providers:
    - devin
    - goose
  
  provider_features:
    devin:
      - modules
    goose:
      - modules
  
  method: "symlink"

metadata:
  tags:
    - my-package
    - example
  
  maintainers:
    - name: "Your Name"
      email: "your@email.com"
  
  status: "stable"
```

### 3. Implement Features

Implement your agents, skills, modules, etc. in the appropriate directories.

### 4. Add Documentation

Create `packages/my-package/README.md` with usage instructions and examples.

### 5. Add Tests

Add tests for all components (minimum 90% coverage).

### 6. Update Registry Index

Add your package to `package-index.yaml`:

```yaml
packages:
  - name: "my-package"
    version: "1.0.0"
    description: "My awesome package"
    author: "Your Name"
    license: "MIT"
    category: "utilities"
    tags:
      - my-package
      - example
    path: "packages/my-package"
    url: "https://github.com/lleite/cockpit-registry/tree/main/packages/my-package"
    supported_providers:
      - devin
      - goose
    features:
      - modules
    requirements:
      cockpit: ">=0.2.0"
    status: "stable"
    released_at: "2026-06-20T10:00:00Z"
```

### 7. Submit Pull Request

1. Fork this repository
2. Create a feature branch
3. Add your package
4. Update `package-index.yaml`
5. Submit a pull request

## Contributing

We welcome contributions! To contribute a package:

1. **Fork** this repository
2. **Create** a new branch for your package
3. **Implement** your package following the structure above
4. **Test** thoroughly (minimum 90% coverage)
5. **Document** with README and usage guides
6. **Update** `package-index.yaml`
7. **Submit** a pull request

### Package Requirements

- Package name must be lowercase with hyphens
- Must have valid `cockpit-package.yml`
- Must have comprehensive README.md
- Must have LICENSE file (MIT recommended)
- Must have tests for all components
- Must support at least one provider
- Must follow AICockpit package specification
- Must be documented in `package-index.yaml`

## Registry Management

### List Registries

```bash
cockpit pkg registries list
```

### Add Registry

```bash
cockpit pkg registries add my-registry https://github.com/user/packages
```

### Update Registry Cache

```bash
cockpit pkg registries update official
```

## Support

- **Issues:** https://github.com/lleite/cockpit-registry/issues
- **Discussions:** https://github.com/lleite/cockpit-registry/discussions
- **Documentation:** https://docs.aicockpit.dev/packages

## License

All packages in this registry are licensed under their respective licenses. See individual package LICENSE files for details.

## Maintainers

- AICockpit Team

## Related Documentation

- [Package Specification](https://github.com/lleite/aicockpit/blob/main/ai-assets/knowledge-base/guides/package-specification.md)
- [Package Manager](https://github.com/lleite/aicockpit/blob/main/ai-assets/knowledge-base/guides/package-manager.md)
- [Package Registry](https://github.com/lleite/aicockpit/blob/main/ai-assets/knowledge-base/guides/package-registry.md)
- [AICockpit Documentation](https://docs.aicockpit.dev)
