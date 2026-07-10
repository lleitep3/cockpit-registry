# pkg-playwright

Cockpit package that exposes a persistent, profile-aware Playwright browser server to AI agents via the `cockpit playwright` command.

## Purpose

Allows AI agents (Devin, Goose, Antigravity) to automate browser interactions using a real Chromium instance with a persistent user profile — useful for web scraping, UI testing, and any task that requires navigating authenticated sessions.

## Requirements

| Dependency | Minimum version |
|---|---|
| AICockpit (`cockpit`) | `0.1.0` |
| Node.js | `>=18.0.0` |

Node dependencies (`playwright`, `express`) are installed automatically during `cockpit pkg install`.

## Installation

```bash
cockpit pkg install pkg-playwright
```

The installer will:
1. Copy the package to `~/.cockpit/packages/pkg-playwright/`.
2. Run `npm install` inside the package directory to install Node dependencies.
3. Install Playwright browser binaries (Chromium) on first use.

## Configuration

```bash
cockpit playwright configure
```

Runs the interactive configuration script (sets default browser, profile path, headless mode, etc.).

## Validation

```bash
cockpit playwright validate
```

Checks that Node.js, npm, and the Playwright package are correctly installed and the configuration is valid.

## Usage

### Start a browser session

```bash
# Open a browser and navigate to a URL
cockpit playwright start --url https://example.com

# Use a specific browser
cockpit playwright start --browser firefox --url https://example.com

# Headless mode
cockpit playwright start --headless --url https://example.com
```

### From an AI agent

After installation the `playwright` command is registered in the cockpit CLI. Agents can call:

```
cockpit playwright start --url <target>
```

The process starts an Express HTTP server that accepts JSON commands (navigate, click, fill, screenshot, etc.) on `localhost:3456` and forwards them to the Playwright context.

## Browser profile

The persistent profile is stored at `~/.cockpit/browser_profile/` by default. This preserves cookies, local storage, and logged-in sessions across runs.

Override with:

```bash
cockpit playwright start --profile /path/to/custom/profile
```

## Package structure

```
pkg-playwright/
├── bin/
│   ├── playwright   # Node.js entry point
│   ├── configure    # Interactive configuration script
│   └── validate     # Validate Node + Playwright installation
├── package.json
├── cockpit-package.yml
└── README.md
```

## Supported providers

`antigravity`, `devin`, `goose`

## License

MIT
