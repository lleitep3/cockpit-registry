# Database Guide — PostgreSQL + Alembic

## Stack

| Tecnologia | Versão | Papel                         |
|------------|--------|-------------------------------|
| PostgreSQL | 16     | Banco de dados relacional     |
| asyncpg    | latest | Driver async nativo           |
| SQLAlchemy | 2.0    | ORM com suporte async         |
| Alembic    | latest | Migrations versionadas        |

## Persistência de Dados

Os dados do PostgreSQL ficam em `./db/data/` — um bind mount no host.

```yaml
# docker-compose.yml
volumes:
  - ./db/data:/var/lib/postgresql/data
```

**Nunca use volumes Docker anônimos** (`- postgres_data:/var/...`). O bind mount garante:
- Dados visíveis e inspecionáveis no host
- Persistência após `docker-compose down`
- Backup simples (copiar a pasta)

A pasta `db/data/` está no `.gitignore` do boilerplate.

## `core/database.py`

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=5,
    max_overflow=10,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass

async def init_db() -> None:
    # Apenas para desenvolvimento sem migrations. Em produção, use Alembic.
    from app.models import item  # noqa: F401 - importa para registrar metadata
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

## SQLAlchemy Model (exemplo)

```python
# models/item.py
from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
```

## Alembic — Migrations

### Gerar migration após alterar models

```bash
# Dentro do container backend
podman-compose exec backend alembic revision --autogenerate -m "add items table"

# Aplicar migrations
podman-compose exec backend alembic upgrade head

# Ver histórico
podman-compose exec backend alembic history

# Reverter última migration
podman-compose exec backend alembic downgrade -1
```

### `alembic/env.py` — Configuração async

```python
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from app.core.config import settings
from app.core.database import Base
import app.models  # noqa: F401 - registra todos os models

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
```

## Variáveis de Ambiente do Banco

```env
# .env
DB_USER=miniapp
DB_PASS=miniapp
DB_NAME=miniapp
DB_PORT=5432
DATABASE_URL=postgresql+asyncpg://miniapp:miniapp@db:5432/miniapp
```
