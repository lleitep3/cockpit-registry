---
name: {PKG_NAME}
description: "Teaches AI agents how to use the {PKG_NAME} package"
---

# {PKG_NAME}

Use this skill when the user asks to run the `{PKG_NAME}` command.

## Command

```bash
cockpit {PKG_NAME} hello
```

## Output

The command prints a hello message.

## Best Practices

- Update this skill as the package evolves.
- Keep instructions concise and action-oriented.


## Configuration and evidence

Before adding credentials, check `cockpit config --help`. Keep public settings in
this package namespace and secrets in the vault; use an explicit account profile.
Do not pass secret values in arguments or print them. A namespace is not an OS
sandbox, and a dependency does not grant access to another package's namespace.
State which checks are simulated and which were validated against the real service.
