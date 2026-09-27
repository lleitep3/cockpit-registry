# {PKG_NAME}

Short description of this AICockpit package.

## Install

```bash
cockpit pkg install {PKG_NAME}
```

For local development:

```bash
cp -r ~/.cockpit/local-registry/{PKG_NAME} ~/.cockpit/packages/
cockpit deploy
```

## Usage

```bash
cockpit {PKG_NAME} hello
```

## Features

- CLI command exposed as `cockpit {PKG_NAME}`
- Skill for AI agents under `skills/{PKG_NAME}/SKILL.md`

## Development

- Edit `lib/command.sh` to implement the command logic.
- Update `cockpit-package.yml` metadata, features, and dependencies.
- Add tests in `tests/run_test.sh`.
- Validate with `cockpit cockpit-builder validate ~/.cockpit/local-registry/{PKG_NAME}`.


## Configuration contract

Use the shared `cockpit config` profile service when configuration is needed.
Declare the minimum supported Cockpit version after checking the actual release.
Public settings and secret references belong to this package namespace; credentials
stay in the vault. Test denied cross-package reads and locked-vault behavior.
The Bash scaffold does not establish native Windows support.
