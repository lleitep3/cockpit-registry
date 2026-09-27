---
name: cockpit-package-builder
description: "Teaches AI agents to create AICockpit packages using cockpit-builder and official conventions"
---

# Cockpit Package Builder

Use this skill when the user asks to:
- Create a new AICockpit package
- Scaffold a cockpit package
- Validate a cockpit package
- Understand the structure of a cockpit package

## Commands

Create a new package in the local registry:

```bash
cockpit cockpit-builder create <package-name>
```

Create a package in a custom path:

```bash
cockpit cockpit-builder create <package-name> /custom/output/path
```

Validate a package:

```bash
cockpit cockpit-builder validate <package-path>
```

Create a new package registry:

```bash
cockpit cockpit-builder registry create <path> [--remote URL]
```

Validate a registry:

```bash
cockpit cockpit-builder registry validate <registry-path>
```

Publish a package into a registry:

```bash
cockpit cockpit-builder publish <package-path> <registry-path>
```

## Package conventions

- Develop all new packages in `~/.cockpit/local-registry/<package-name>`.
- Every package must have a `cockpit-package.yml` manifest.
- CLI modules live in `bin/` and must be executable.
- Skills live in `skills/<skill-name>/SKILL.md`.
- README.md is required.
- Follow semver for versions (e.g., `0.1.0`).
- Package names must be lowercase with hyphens.

## Registry conventions

- Registry repositories must have a `package-index.yaml` at the root.
- Packages in a registry must live under `packages/<package-name>/`.
- A GitHub Actions workflow at `.github/workflows/validate-packages.yml` validates PRs.
- The `scripts/validate_packages.py` script validates the registry locally.
- The `scripts/validate_pr.py` script enforces contribution rules: one package per PR, version bump required, version bump must match PR commits.

## Registry contribution rules

Generated registries include:

- `scripts/validate_pr.py`
- `.github/workflows/validate-packages.yml` with two jobs:
  - `validate` — runs `scripts/validate_packages.py`
  - `validate-pr` — runs `scripts/validate_pr.py`

The `validate-pr` job enforces:

- One package per PR
- Version bump required for package updates
- Version bump must match PR commit scope

## Default boilerplate

The `create` subcommand generates a complete package from:

```
~/.cockpit/local-registry/cockpit-package-builder/boilerplates/default/
```

The generated package includes:
- `cockpit-package.yml`
- `README.md`
- `bin/<package-name>`
- `lib/command.sh`
- `bin/configure`
- `bin/validate`
- `skills/<package-name>/SKILL.md`
- `tests/run_test.sh`

## Best practices

1. After creating the package, edit the manifest metadata and description.
2. Implement the real logic in `lib/command.sh`.
3. Add or remove subcommands in `bin/<package-name>` as needed.
4. Validate the package before installing locally.
5. Use `cockpit cockpit-builder publish` to add/update the package in a registry.
6. If the registry has a remote, the builder creates a feature branch and opens a PR.


## Evolution contract

For existing packages and core/package decisions, follow
[the evolution workflow](references/evolution-workflow.md). Read
[package profiles](references/package-profiles.md) before adding configuration or
credentials. Detect `cockpit config --help` first; older cores must fail with an
upgrade instruction instead of silently falling back to plaintext storage.

This builder validates structure and shell syntax, not live API behavior. Run the
package's behavioral tests separately. Test negative fixtures: missing/escaping
feature paths, malformed scripts, missing dependencies and locked vault access.
Distinguish local fixtures, real browser login, external API validation and CI.
Never copy personal browser cookies or bypass administrative browser restrictions.

The default boilerplate is Bash-based; do not advertise native Windows support
without a separate implementation and test. Update provider declarations only for
assets supported by the provider. Avoid unrelated global rules and copied docs;
keep detailed guidance in references and route there from this skill.

`publish` can create commits, push and open a PR. Inspect its help/source and the
registry policy before invoking it. Package dependencies never grant namespace
access. Shared secrets require an explicit operator grant and an unlocked vault.
