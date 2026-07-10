# pkg-scheduler

`pkg-scheduler` is an AICockpit plugin that adds a `scheduler` command to the CLI. It lets you schedule commands and scripts to run later, on a cron pattern, daily, on weekends, or a finite number of times. Jobs are persisted to JSON so they survive restarts.

## Features

- Schedule any shell command or script
- Cron expressions (5 fields: minute hour day month weekday)
- Presets: `--daily` and `--weekends` at 09:00 UTC
- Finite repetitions: `--repeat N`
- List active jobs with next run time and run count
- Remove jobs by ID
- Run pending jobs on demand
- Install a systemd user timer (Linux) or launchd agent (macOS) that runs every minute
- Show scheduler statistics
- Persist jobs between reboots in `~/.cockpit/workspace/scheduler/jobs.json`

## Requirements

- AICockpit CLI `>=0.1.0`
- `bash`
- `python3` or `jq` for JSON persistence (used by `bin/scheduler`)
- `systemd` (Linux) or `launchd` (macOS) for automatic execution via `install`

## Installation

Install the package with AICockpit:

```bash
cockpit install pkg-scheduler
```

This copies the scripts into the AICockpit modules path so `cockpit scheduler` becomes available.

## Configuration

Configure the default run time and workspace directory:

```bash
# Change default daily/weekend time to 14:30
cockpit scheduler configure --time 14:30

# Use a custom workspace directory
cockpit scheduler configure --workspace ~/.my-scheduler
```

Default workspace is `~/.cockpit/workspace/scheduler` and default time is `09:00`.

## Commands

### `add`

Schedule a command.

```bash
# Cron expression: weekdays at 09:00
cockpit scheduler add "cockpit deploy" --cron "0 9 * * 1-5"

# Run 3 times (every minute by default)
cockpit scheduler add "echo hello" --repeat 3

# Every day at 09:00
cockpit scheduler add "scripts/backup.sh" --daily

# Every Saturday and Sunday at 09:00
cockpit scheduler add "scripts/weekend-report.sh" --weekends

# With a friendly name
cockpit scheduler add "make test" --cron "0 8 * * 1-5" --name "morning-tests"
```

### `list`

List all scheduled jobs.

```bash
cockpit scheduler list
```

Shows ID, name, command, schedule, next run, run count and max runs.

### `remove`

Remove a job by ID.

```bash
cockpit scheduler remove <id>
```

### `run`

Execute pending jobs. This is normally called by the installed timer every minute, but you can run it manually.

```bash
cockpit scheduler run
```

A job is executed if:

- Its cron expression matches the current UTC minute, or
- Its `next_run` timestamp is less than or equal to now.

After execution, `last_run` and `run_count` are updated. Jobs with `--repeat N` are removed when `run_count` reaches `max_runs`.

### `install`

Install a systemd user timer on Linux or a launchd plist on macOS. The timer runs `cockpit scheduler run` every minute.

```bash
# Linux
cockpit scheduler install
systemctl --user daemon-reload
systemctl --user enable --now cockpit-scheduler.timer

# macOS
cockpit scheduler install
launchctl load ~/Library/LaunchAgents/dev.aicockpit.scheduler.plist
```

### `status`

Show scheduler statistics.

```bash
cockpit scheduler status
```

### `configure`

Set default run time and workspace directory.

```bash
cockpit scheduler configure --time 14:30 --workspace ~/.my-scheduler
```

### `validate`

Check that the workspace directory exists and that `jobs.json` is valid JSON (if present).

```bash
cockpit scheduler validate
```

## Persistence format

Jobs are stored as a JSON array in `~/.cockpit/workspace/scheduler/jobs.json`:

```json
[
  {
    "id": "uuid",
    "name": "tag",
    "command": "cockpit deploy",
    "cron": "0 9 * * 1-5",
    "next_run": "2024-01-15T09:00:00Z",
    "last_run": null,
    "run_count": 0,
    "max_runs": null,
    "created_at": "2024-01-15T08:00:00Z"
  }
]
```

- `id`: unique identifier
- `name`: optional user tag
- `command`: shell command to execute
- `cron`: cron expression or `null` for repeat jobs
- `next_run`: ISO 8601 UTC timestamp of the next planned execution
- `last_run`: ISO 8601 UTC timestamp of the last execution or `null`
- `run_count`: number of times the job has already run
- `max_runs`: maximum number of runs for `--repeat` jobs, otherwise `null`
- `created_at`: ISO 8601 UTC timestamp when the job was created

## File structure

```
packages/pkg-scheduler/
├── cockpit-package.yml   # Package manifest
├── README.md             # This file
└── bin/
    ├── scheduler         # Main command (add, list, remove, run, install, status)
    ├── configure         # Default time and workspace configuration
    └── validate          # Workspace and JSON validation
```

## Cron format

Five space-separated fields:

```
minute hour day month weekday
```

Examples:

| Expression       | Meaning                              |
|------------------|--------------------------------------|
| `0 9 * * 1-5`    | Weekdays at 09:00                    |
| `0 9 * * 0,6`    | Weekends at 09:00                    |
| `0 9 * * *`      | Every day at 09:00                   |
| `*/5 * * * *`    | Every 5 minutes                        |
| `0 2 1 * *`      | First day of the month at 02:00      |

Supported cron syntax includes `*`, exact numbers, ranges (`1-5`), lists (`1,3,5`) and steps (`*/5`).

## License

MIT
