# cockpit-scheduler

Pacote do AICockpit para agendamento de comandos e scripts.

## Install

```bash
cockpit pkg install cockpit-scheduler
```

Para desenvolvimento local:

```bash
cp -r ~/.cockpit/local-registry/cockpit-scheduler ~/.cockpit/packages/
cockpit deploy
```

## Usage

### Agendar com cron

```bash
cockpit scheduler add --command "echo 'Hello'" --cron "0 9 * * *"
```

### Agendar com intervalo e repeticoes finitas

```bash
cockpit scheduler add --command "scripts/backup.sh" --interval 1h --repeat 3
```

### Agendar analise diaria de seguranca do Ubuntu

```bash
cockpit scheduler add-ubuntu-security --cron "0 2 * * *"
```

### Listar agendamentos

```bash
cockpit scheduler list
```

### Remover agendamento

```bash
cockpit scheduler remove <id>
```

### Executar agendamentos pendentes

```bash
cockpit scheduler run
```

### Instalar executor automatico

O modo padrão é `systemd` com `Persistent=true`, garantindo que jobs atrasados
rodem apos o boot.

```bash
# Padrao: systemd, persistent=true
cockpit scheduler install
systemctl --user daemon-reload
systemctl --user enable --now aicockpit-scheduler.timer

# Desabilitar persistencia (nao executa jobs atrasados apos boot)
cockpit scheduler install --persistent false

# Modo cron (sem persistencia automatica)
cockpit scheduler install --mode cron --interval 5
crontab ~/.cockpit/scheduler/cron.txt
```

## Persistencia

Os agendamentos sao salvos em `~/.cockpit/scheduler/jobs.json`.

## Padrões de cron suportados

- Expressoes padrao: `0 9 * * *`
- Aliases: `@daily`, `@hourly`, `@weekly`, `@monthly`, `@yearly`
- Extensoes: `daily`, `hourly`, `weekdays`, `weekends`
- Intervalos: `1h`, `30m`, `5m`, `1d`, `1w`, `2h`, `10s`

## Development

- Edite arquivos em `~/.cockpit/local-registry/cockpit-scheduler/`
- Torne scripts executaveis: `chmod +x bin/scheduler lib/*.sh`
- Teste localmente com `cockpit scheduler list`
