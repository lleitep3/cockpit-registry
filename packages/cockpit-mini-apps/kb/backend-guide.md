# Backend Guide — FastAPI async

## Stack

| Tecnologia       | Versão  | Papel                          |
|------------------|---------|--------------------------------|
| FastAPI          | latest  | Framework web async            |
| SQLAlchemy       | 2.0     | ORM async                      |
| asyncpg          | latest  | Driver PostgreSQL async        |
| Alembic          | latest  | Migrations                     |
| pydantic-settings| latest  | Config via variáveis de env    |
| structlog        | latest  | Logging estruturado            |
| uvicorn          | latest  | ASGI server                    |

## Estrutura do Projeto

```
app/
├── main.py             # FastAPI app, lifespan, CORS, inclusão de routers
├── core/
│   ├── config.py       # pydantic-settings (lê .env automaticamente)
│   ├── database.py     # engine async + AsyncSession factory
│   └── logging.py      # structlog configurado
├── models/
│   └── item.py         # SQLAlchemy model (exemplo: Item)
├── schemas/
│   └── item.py         # Pydantic schemas: ItemCreate, ItemRead, ItemUpdate
├── routers/
│   ├── health.py       # GET /health
│   └── items.py        # CRUD completo
└── services/
    └── item_service.py # lógica de negócio isolada do router
```

## `main.py` — App Principal

```python
from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.core.logging import setup_logging
from app.routers import health, items

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await init_db()
    logger.info("startup", app=settings.APP_NAME)
    yield
    logger.info("shutdown")

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(items.router, prefix="/api/v1")
```

## `core/config.py` — Configuração

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "mini-app"
    DATABASE_URL: str = "postgresql+asyncpg://miniapp:miniapp@db:5432/miniapp"
    DEBUG: bool = False
    LOG_FORMAT: str = "pretty"  # "pretty" em dev, "json" em prod

settings = Settings()
```

## `core/logging.py` — Logging com structlog

```python
import logging
import structlog
from app.core.config import settings

def setup_logging() -> None:
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    if settings.LOG_FORMAT == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.DEBUG if settings.DEBUG else logging.INFO
        ),
    )
```

## Endpoints do CRUD de Exemplo

| Método | Rota                | Descrição                  |
|--------|---------------------|----------------------------|
| GET    | `/health`           | Healthcheck (valida o DB)  |
| GET    | `/api/v1/items`     | Lista paginada             |
| POST   | `/api/v1/items`     | Cria item                  |
| GET    | `/api/v1/items/{id}`| Busca por ID               |
| PATCH  | `/api/v1/items/{id}`| Atualização parcial        |
| DELETE | `/api/v1/items/{id}`| Remove item                |

### Parâmetros de paginação (GET /items)

```
?skip=0&limit=20
```

## Swagger e ReDoc

FastAPI expõe automaticamente:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

Não é necessária nenhuma configuração extra.

## Healthcheck

```python
# routers/health.py
@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
    return {"status": "ok", "db": db_status}
```

## Dependency Injection — AsyncSession

```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

## Padrão dos Routers

```python
# routers/items.py
import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate
from app.services import item_service

logger = structlog.get_logger()
router = APIRouter(prefix="/items", tags=["items"])

@router.get("/", response_model=list[ItemRead])
async def list_items(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    logger.info("list_items", skip=skip, limit=limit)
    return await item_service.list_items(db, skip=skip, limit=limit)
```
