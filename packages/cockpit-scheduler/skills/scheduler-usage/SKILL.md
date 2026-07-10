# Scheduler Usage

Use o comando `cockpit scheduler` para agendar comandos e scripts no AICockpit.

## Comandos principais

```bash
# Agendar comando com cron
cockpit scheduler add --command "echo hello" --cron "0 9 * * *"

# Agendar comando com intervalo e repeticoes finitas
cockpit scheduler add --command "backup.sh" --interval 1h --repeat 3

# Agendar analise diaria do ubuntu-security
cockpit scheduler add-ubuntu-security --cron "0 2 * * *"

# Listar, remover e executar
cockpit scheduler list
cockpit scheduler remove <id>
cockpit scheduler run
```

## Instalar executor automatico

```bash
# Systemd timer
cockpit scheduler install --mode systemd --interval 5
systemctl --user daemon-reload
systemctl --user enable --now aicockpit-scheduler.timer

# Cron
cockpit scheduler install --mode cron --interval 5
crontab ~/.cockpit/scheduler/cron.txt
```

## Persistencia

Agendamentos ficam em `~/.cockpit/scheduler/jobs.json`.

## Padrões suportados

- Cron: `0 9 * * *`, `@daily`, `@hourly`, `weekdays`, `weekends`
- Intervalos: `1h`, `30m`, `5m`, `1d`, `1w`, `2h`, `10s`
