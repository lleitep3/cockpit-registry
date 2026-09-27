:_cockpit-package-builder

AICockpit package for scaffolding, validating, and configuring new AICockpit packages.

## Install

```bash
cockpit pkg install cockpit-package-builder
```

For local development:

```bash
cp -r ~/.cockpit/local-registry/cockpit-package-builder ~/.cockpit/packages/
cockpit deploy
```

## Usage

### Create a new package

```bash
cockpit cockpit-builder create my-tool
```

The package is created under `~/.cockpit/local-registry/my-tool`.

### Create a package in a custom path

```bash
cockpit cockpit-builder create my-tool /custom/output/path
```

### Validate a package

```bash
cockpit cockpit-builder validate ~/.cockpit/local-registry/my-tool
```

### Configure the builder

```bash
cockpit cockpit-builder configure
```

## Subcommands

### Package commands

- `create <name> [path]` — scaffold a new package from the default boilerplate
- `validate <path>` — validate a package against official conventions
- `configure` — show builder configuration info

### Registry commands

- `registry create <path> [--remote URL]` — create a new package registry repository
- `registry validate <path>` — validate a registry
- `publish <package-path> <registry-path>` — publish or update a package in a registry

### Help

- `help` — show help

## Registry contribution rules

Generated registries include `scripts/validate_pr.py` and a GitHub Actions workflow with two jobs:

- `validate` — runs `scripts/validate_packages.py`
- `validate-pr` — runs `scripts/validate_pr.py`

The `validate-pr` job enforces contribution rules:

- One package per PR
- Version bump required for package updates
- Version bump must match PR commit scope

## Boilerplate

The default boilerplate is stored in:

```
boilerplates/default/
```

It includes a complete package structure with:
- manifest
- README
- CLI wrapper
- command implementation
- `configure` and `validate` scripts
- skill template
- test runner

## Development

- Edit `lib/create.sh` to change package scaffolding behavior.
- Edit `lib/validate.sh` to change package validation rules.
- Edit `lib/registry_create.sh` to change registry creation.
- Edit `lib/registry_validate.sh` to change registry validation.
- Edit `lib/publish.sh` to change publishing behavior.
- Add new boilerplates under `boilerplates/` if needed.


## Validation and shared configuration

Validation fails on missing/escaping feature paths and invalid shell syntax.
Python 3 plus PyYAML are required in the runtime; validation does not install them.
Run `bash tests/run_test.sh` for scaffold, negative-fixture and local publication
tests. External API/browser validation is separate and needs authorized access.

Use the skill references for shared profile/vault configuration and the evolution
workflow. Detect `cockpit config --help`; the new contract requires a core release
containing that command. This package remains usable for scaffolding on older cores.
Namespaces prevent accidental CLI access, not hostile same-user process access.
