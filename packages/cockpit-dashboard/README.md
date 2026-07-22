# cockpit-dashboard

Mini-app visual que mostra o estado atual do AICockpit em tempo real.

## Instalação

```bash
cockpit pkg install cockpit-dashboard
```

## Uso

```bash
# Abre o dashboard no browser
cockpit dashboard open

# Para o dashboard
cockpit dashboard stop

# Ver logs
cockpit dashboard logs
```

## Módulos implementados

| Módulo | Rota | Descrição |
|--------|------|-----------|
| **Visão Geral** | `/` | KPIs com links para outros módulos e diagnósticos via `cockpit doctor --json`. |
| **Pacotes** | `/packages` | Abas Instalados/Registry, busca fuzzy, drawer de detalhes e instalação assíncrona com SSE. |
| **Vault** | `/vault` | Status do vault, lock/unlock, senha mestra, credenciais com reveal/copy e auto-lock por inatividade. |
| **Knowledge Base** | `/kb` | Lista de documentos, grafo interativo D3 de notas e links, busca e preview drawer. |
| **Mini-Apps** | `/mini-apps` | Cards de processos, logs SSE, ações start/stop/restart e métricas de CPU/memória. |
| **Logs & Insights** | `/logs` | Análise de logs e métricas de execução dos comandos do cockpit. |

## Recursos gerais

- **Sidebar** com navegação entre 6 telas.
- **Responsividade mobile** com drawer.
- **Command palette** (`Ctrl+K`) para navegação rápida.
- **CommandExecutor** no backend para executar comandos do cockpit whitelistados com segurança.
- **Testes backend** com pytest: cobertura >= 90%.

## Stack

| Camada | Tecnologia |
|--------|------------|
| Frontend | SvelteKit + Tailwind CSS |
| Backend | FastAPI (Python 3.12) |
| Gráficos | D3.js |

## URLs

- Frontend: http://localhost:3000
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

## Workspace

O mini-app é copiado para:

```
~/.cockpit/workspace/cockpit-dashboard/
├── app/
│   ├── backend/
│   └── frontend/
├── .venv/
└── .env
```

Sem Docker. Para stacks com banco de dados, use o boilerplate do `cockpit-mini-apps` com DB.

## Testes

```bash
cd app/backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=90
```
