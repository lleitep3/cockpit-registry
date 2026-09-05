# github-tools

AICockpit package that wraps the official GitHub CLI (`gh`) with vault-backed authentication and multi-profile support.

## Supported `gh` version

Tested with `gh >= 2.50.0`. Older versions may work but are not guaranteed.

## Installation

```bash
cockpit pkg install github-tools
```

## Configure profiles

A profile binds a GitHub username to a token. You can register several profiles and choose one as default.

```bash
# Add a profile (also validates the token against GitHub)
cockpit github configure --user <USER> --token <GITHUB_TOKEN>

# Set a profile as the default one
cockpit github configure --user <USER> --token <GITHUB_TOKEN> --default

# List configured profiles
cockpit github configure --list

# Remove a profile
cockpit github configure --remove --user <USER>

# Keep a single default profile (legacy behaviour)
cockpit github configure --token <GITHUB_TOKEN>
```

You can also store a default owner/repo for repository resolution:

```bash
cockpit github configure --user <USER> --token <TOKEN> \
                         --default-owner <OWNER> \
                         --default-repo <REPO> \
                         --default
```

## Usage

```bash
# Use the default profile
cockpit github run repo view

# Use a specific profile for one command
cockpit github --user <USER> run repo view

# Run any gh command with the selected token injected
cockpit github run <gh args...>

# Run git commands with the profile's name/email as author
# (useful when you need to commit as a specific GitHub user)
cockpit github --user <USER> git commit -m "my commit"

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
