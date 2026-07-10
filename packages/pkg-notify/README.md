# pkg-notify

Native and HTML notifications for AI agents running inside AICockpit.

This package exposes the `cockpit notify` command so an agent can surface
important events to the user via the operating system's native notification
system or through a temporary HTML page opened in the browser.

## Purpose

- Notify the user without interrupting the agent's workflow.
- Provide a fallback channel when native notifications are unavailable or
  need richer formatting.
- Keep a small local history of recent notifications for quick inspection.

## Requirements

- AICockpit `>= 0.1.0`
- One of the supported OS/tool combinations:
  - **Linux:** `notify-send` (libnotify) and `xdg-open`
  - **macOS:** `osascript` and `open`
  - **Windows:** `powershell` and `start`
- `jq` for history and configuration management

## Installation

```bash
cockpit install pkg-notify
```

Or, for a manual local copy:

```bash
cp -r packages/pkg-notify ~/.cockpit/packages/pkg-notify
chmod +x ~/.cockpit/packages/pkg-notify/bin/*
```

## Configuration

Run the interactive configuration script to choose the default channel:

```bash
cockpit notify configure
```

It will ask for `native` or `html` and save the choice to:

```
~/.cockpit/packages/pkg-notify/config.json
```

Example:

```json
{
  "channel": "native"
}
```

To validate that the configured channel works on the current machine:

```bash
cockpit notify validate
```

## CLI Usage

### Send a native notification

```bash
cockpit notify send --title "Build done" --message "All tests passed"
```

With an optional link:

```bash
cockpit notify send --title "Deploy finished" \
                    --message "Production is ready" \
                    --action-url "https://dashboard.example.com"
```

### Generate and open an HTML notification

```bash
cockpit notify html --title "Report ready" --message "Your daily report is available."
```

Use the dark template:

```bash
cockpit notify html --title "Report ready" --message "Your daily report is available." --template dark
```

### Show recent notification history

```bash
cockpit notify status
```

History is stored in:

```
~/.cockpit/workspace/notify/history.json
```

## AI Agent Usage

An AI agent can surface notifications naturally:

```text
I need to notify the user that the task is complete.
```

The agent can invoke:

```bash
cockpit notify send --title "Task complete" --message "The requested analysis is done."
```

Or, when richer formatting is needed:

```bash
cockpit notify html --title "Analysis report" --message "Long-form results are available." --template dark
```

## File Structure

```
packages/pkg-notify/
├── cockpit-package.yml    # Package manifest
├── README.md              # This file
└── bin/
    ├── notify             # Main CLI script (send, html, status)
    ├── configure          # Interactive default channel setup
    └── validate           # Check native/HTML tooling availability
```

Runtime files:

```
~/.cockpit/packages/pkg-notify/config.json   # User configuration
~/.cockpit/workspace/notify/history.json     # Notification history
~/.cockpit/workspace/notify/notify-*.html    # Temporary HTML notifications
```

## Supported Providers

| Provider   | Native | HTML | Notes                         |
|------------|--------|------|-------------------------------|
| antigravity | yes   | yes  | Copy install                  |
| devin      | yes    | yes  | Copy install                  |
| goose      | yes    | yes  | Copy install                  |

## License

MIT
