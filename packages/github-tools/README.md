# github-tools

AICockpit package that wraps the official GitHub CLI (`gh`) with vault-backed authentication.

## Supported `gh` version

Tested with `gh >= 2.50.0`. Older versions may work but are not guaranteed.

## Installation

```bash
cockpit pkg install github-tools
```

## Configure

```bash
cockpit github configure --token <GITHUB_TOKEN> \
                         --default-owner <OWNER> \
                         --default-repo <REPO>
```

The configure step:

1. Checks that `gh` is installed.
2. Validates that the supplied token can authenticate against GitHub.
3. Stores the token securely in the AICockpit vault under the namespace `github-tools`.
4. Optionally stores the default owner and repository for subsequent commands.

## Usage

```bash
# Pass any gh command with the token injected automatically
cockpit github run <gh args...>

# GitHub Actions
cockpit github actions list [--repo OWNER/REPO] [--limit N]
cockpit github actions watch <run-id> [--repo OWNER/REPO]
cockpit github actions logs <run-id> [--repo OWNER/REPO]

# Commits
cockpit github commits <branch> [--repo OWNER/REPO] [--limit N]

# Pull requests
cockpit github pr comment <pr> --body "..." [--repo OWNER/REPO]
cockpit github pr approve <pr> [--repo OWNER/REPO]
cockpit github pr resolve <pr> [--repo OWNER/REPO]
```

If `--repo` is omitted, the command falls back to the configured default or detects the repository from the current Git directory.
