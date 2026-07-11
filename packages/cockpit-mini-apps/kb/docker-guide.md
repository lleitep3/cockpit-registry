# Docker Guide — Podman e Docker Compose

## Runtime Detectado Automaticamente

O CLI `cockpit mini-app` detecta automaticamente o runtime disponível:

1. **Podman** (preferido): se `podman` estiver no PATH, usa `podman-compose`
2. **Docker** (fallback): se podman não estiver disponível, usa `docker compose`

Você não precisa fazer nada — o comando correto é executado automaticamente.

## `docker-compose.yml` — with-db (3 serviços)

```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "${FRONTEND_PORT:-3000}:3000"
    environment:
      - VITE_API_URL=http://localhost:${BACKEND_PORT:-8000}
    depends_on:
      backend:
        condition: service_healthy
    volumes:
      - ./frontend:/app
      - /app/node_modules   # evita sobrescrever node_modules do host
    restart: unless-stopped

  backend:
    build: ./backend
    ports:
      - "${BACKEND_PORT:-8000}:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://${DB_USER:-miniapp}:${DB_PASS:-miniapp}@db:5432/${DB_NAME:-miniapp}
      - LOG_FORMAT=${LOG_FORMAT:-pretty}
      - DEBUG=${DEBUG:-true}
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./backend:/app      # hot-reload: edições locais refletem no container
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=${DB_USER:-miniapp}
      - POSTGRES_PASSWORD=${DB_PASS:-miniapp}
      - POSTGRES_DB=${DB_NAME:-miniapp}
    volumes:
      - ./db/data:/var/lib/postgresql/data   # dados no host, não em volume anônimo
    ports:
      - "${DB_PORT:-5432}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-miniapp}"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: unless-stopped
```

## `docker-compose.yml` — without-db (2 serviços)

```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "${FRONTEND_PORT:-3000}:3000"
    environment:
      - VITE_API_URL=http://localhost:${BACKEND_PORT:-8000}
    depends_on:
      backend:
        condition: service_healthy
    volumes:
      - ./frontend:/app
      - /app/node_modules
    restart: unless-stopped

  backend:
    build: ./backend
    ports:
      - "${BACKEND_PORT:-8000}:8000"
    environment:
      - LOG_FORMAT=${LOG_FORMAT:-pretty}
      - DEBUG=${DEBUG:-true}
    volumes:
      - ./backend:/app
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
```

## Comandos Úteis

```bash
# Subir tudo (detecta podman ou docker automaticamente via cockpit)
cockpit mini-app new <nome>

# Comandos manuais dentro da pasta do projeto
cd ~/.cockpit/workspace/mini-apps/<nome>

# Subir
podman-compose up --build -d
# ou
docker compose up --build -d

# Ver logs
podman-compose logs -f
podman-compose logs -f backend
podman-compose logs -f frontend

# Parar
podman-compose down

# Parar e remover volumes (APAGA DADOS DO DB)
podman-compose down -v

# Restart de um serviço
podman-compose restart backend

# Executar comando no container
podman-compose exec backend alembic upgrade head
podman-compose exec backend python -c "from app.core.config import settings; print(settings)"
```

## Hot-Reload em Desenvolvimento

O hot-reload funciona via volumes montados:

- **Frontend**: Vite detecta mudanças em `./frontend/src/` e recarrega o browser automaticamente
- **Backend**: uvicorn com `--reload` detecta mudanças em `./backend/app/` e reinicia o servidor

Não é necessário reconstruir os containers para mudanças de código — apenas para mudanças em `requirements.txt` ou `package.json`.

## Reconstruir após mudar dependências

```bash
# Instalar nova dependência Python
echo "nova-lib==1.0.0" >> backend/requirements.txt
podman-compose up --build -d backend

# Instalar nova dependência Node
cd frontend && npm install nova-lib
podman-compose up --build -d frontend
```

## Portas em Conflito

Se as portas padrão estiverem em uso, edite o `.env`:

```env
FRONTEND_PORT=3001
BACKEND_PORT=8001
DB_PORT=5433
```
