# Contributing to Cockpit Registry

## Protected Areas

The following directories contain core infrastructure and validation scripts. Changes to them require review from the registry maintainer:

- `.github/` — GitHub workflows, issue templates, and repository configuration
- `scripts/` — validation scripts and git hooks

Pull requests that modify files under `.github/` or `scripts/` must be approved by `@lleitep3` before merging.

## Package Submission Rules

### PR Requirements

- **One Package Per PR**: Every PR must update exactly one package. PRs updating more than one package will be rejected by CI.
- **Semver Version Bumps**: Any package update must include a semver version bump.
- **Version Bump Scope**: The version bump must match the scope of the PR commits:
  - `feat!` or `BREAKING CHANGE` -> **MAJOR** version bump
  - `feat` -> **MINOR** version bump  
  - `fix`, `docs`, `chore` -> **PATCH** version bump

### How to Submit a Package

1. **Fork** the repository
2. **Create a branch** for your package update
3. **Install git hooks** (recommended): `./scripts/install-hooks.sh`
4. **Update your package** in the `packages/` directory
5. **Bump the version** according to the changes made
6. **Run local validations** (optional): 
   - `./scripts/validate-registry.sh` - validates all packages
   - `./scripts/validate-pr.sh` - validates PR changes
7. **Submit a PR** with clear description of changes
8. **Ensure CI passes** - all validation checks must succeed

### CI Validation

The CI pipeline performs the following checks:

1. **Package Validation** (`validate-packages.yml`):
   - Validates all packages in the registry
   - Checks package structure and metadata
   - Ensures package integrity

2. **PR Validation** (`validate-pr.yml`):
   - Validates that only one package is updated per PR
   - Checks that version bumps match commit types
   - Enforces semver versioning rules
   - Validates conventional commit messages

### Conventional Commits

All commits must follow the conventional commit format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New features (MINOR version bump)
- `fix`: Bug fixes (PATCH version bump)
- `docs`: Documentation changes (PATCH version bump)
- `chore`: Maintenance tasks (PATCH version bump)
- `feat!`: Breaking changes (MAJOR version bump)

**Examples:**
- `feat: add new authentication method` → MINOR bump
- `fix: resolve memory leak in parser` → PATCH bump
- `feat!: remove deprecated API endpoints` → MAJOR bump
- `docs: update installation guide` → PATCH bump

### Version Bump Examples

| Commit Type | Version Change | Example |
|-------------|----------------|---------|
| `feat` | 1.0.0 → 1.1.0 | `feat: add user profile feature` |
| `fix` | 1.0.0 → 1.0.1 | `fix: resolve login issue` |
| `docs` | 1.0.0 → 1.0.1 | `docs: update API documentation` |
| `chore` | 1.0.0 → 1.0.1 | `chore: update dependencies` |
| `feat!` | 1.0.0 → 2.0.0 | `feat!: breaking API changes` |

### Local Development

#### Git Hooks

Install git hooks to automatically run validations before each commit:

```bash
./scripts/install-hooks.sh
```

This will configure git to run validation checks before each commit, ensuring your changes follow the repository standards.

#### Manual Validation

You can run validations manually at any time:

```bash
# Validate all packages in the registry
./scripts/validate-registry.sh

# Validate PR changes (requires git context)
./scripts/validate-pr.sh
```

### Troubleshooting

- **CI fails for multi-package PRs**: Split into separate PRs, one per package
- **Version bump mismatch**: Ensure version bump matches commit types
- **Validation errors**: Check package structure and metadata requirements
- **Pre-commit hook failures**: Run validations manually to identify and fix issues

For questions or issues, please open an issue in the repository.