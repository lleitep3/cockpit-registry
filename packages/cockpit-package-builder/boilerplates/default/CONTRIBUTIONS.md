# Contributing to this Registry

Thank you for contributing to this AICockpit package registry!

## Protected Areas

The following directories contain core infrastructure and validation scripts. Changes to them require review from the registry maintainer:

- `.github/` — GitHub workflows, issue templates, and repository configuration
- `scripts/` — validation scripts and git hooks

Pull requests that modify files under `.github/` or `scripts/` must be approved by `@lleitep3` before merging.

## Pull Request Rules

### One package per PR

Every pull request must update **exactly one** package. PRs that touch multiple packages will be rejected automatically by the CI validation.

### Version bump required

Any update to a package must include a version bump following [Semantic Versioning](https://semver.org/):

- `MAJOR` — breaking changes
- `MINOR` — new features, backward compatible
- `PATCH` — bug fixes, backward compatible

The CI will compare the version in the PR against the version in the registry base branch and reject the PR if no bump is detected.

### Version bump must match the PR commits

The version bump must be consistent with the changes introduced in the PR. The CI validates this by inspecting the commit messages and the modified files:

- `feat!:` or breaking changes → `MAJOR` bump
- `feat:` or new capabilities → `MINOR` bump
- `fix:` or `docs:` or `chore:` → `PATCH` bump

If the bump does not match the scope of the changes, the PR will be rejected.

## Local setup

After cloning this repository, install the git hooks so validation runs automatically before every commit:

```bash
./scripts/install-hooks.sh
```

This sets `core.hooksPath` to `.githooks`. From that point on, every `git commit` will:

1. Run `scripts/validate-registry.sh` — validates the registry structure and all packages.
2. Run `scripts/validate-pr.sh` (on non-`main` branches) — validates PR contribution rules.

## Running validation manually

Validate the registry structure and all packages:

```bash
./scripts/validate-registry.sh
```

Validate PR contribution rules (version bump, one package per PR):

```bash
./scripts/validate-pr.sh
```

## How to submit a package

1. Create or update the package under `packages/<package-name>/`.
2. Ensure the package passes local validation:
   ```bash
   cockpit cockpit-builder validate packages/<package-name>
   ```
3. Update `package-index.yaml` with the new version and metadata.
4. Validate the full registry locally:
   ```bash
   ./scripts/validate-registry.sh
   ```
5. Commit using [Conventional Commits](https://www.conventionalcommits.org/):
   ```bash
   git commit -m "feat(packages): add <package-name> v1.2.3"
   ```
6. Open a pull request from a feature branch.

## CI Checks

All pull requests are validated by `.github/workflows/validate-packages.yml`. The workflow calls:

- `./scripts/validate-registry.sh` — validates the registry structure and every package.
- `./scripts/validate-pr.sh` — ensures only one package is modified per PR, verifies the version was bumped and matches the commit scope.

A PR that fails any of these checks cannot be merged.
