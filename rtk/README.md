# RTK Package for AICockpit

Installs [RTK (Rust Token Killer)](https://github.com/carlosles/rtk) and
configures token-optimized CLI rules for all active AI providers
(Antigravity, Devin, Goose).

## What it does

1. **Downloads and installs** the `rtk` binary to `~/.local/bin`
2. **Configures** each detected AI provider with RTK usage rules:
   - **Antigravity** → `~/.gemini/config/rules/rtk-usage.md`
   - **Goose** → `~/.config/goose/rtk-hints.md`
   - **Devin** → skill deployed via cockpit

## Installation

```bash
cockpit pkg install rtk
```

## Usage

After installation, `rtk` is available as a transparent proxy for any command:

```bash
rtk go test ./...       # 90% token savings
rtk git status          # 70% token savings
rtk gh run list         # 82% token savings
rtk grep pattern path   # 75% token savings

rtk gain                # View total savings
```

## Requirements

- AICockpit >= 0.3.0
- `curl` (for binary download)
- Linux or macOS (x86_64 or aarch64)

## Supported Providers

| Provider | Configuration |
|---|---|
| Antigravity | `~/.gemini/config/rules/rtk-usage.md` |
| Goose | `~/.config/goose/rtk-hints.md` |
| Devin | Skill via cockpit |
