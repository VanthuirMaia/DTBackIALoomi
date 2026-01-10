from pathlib import Path
from dotenv import load_dotenv

# Carrega .env antes de qualquer import que use variaveis de ambiente
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.routes import paints, chat, auth
from app.db.base import Base
from app.db.session import engine

# Importa modelos para garantir que estao registrados no Base
from app.models.paint import Paint  # noqa: F401
from app.models.user import User  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicacao."""
    # Startup: cria tabelas
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: cleanup se necessario
    pass


app = FastAPI(
    title="Assistente Inteligente de Tintas",
    description="API para recomendacao de tintas usando IA com autenticacao JWT",
    version="1.0.0",
    lifespan=lifespan
)


app.include_router(auth.router)
app.include_router(paints.router)
app.include_router(chat.router)


@app.get("/health", tags=["Health"], summary="Health Check")
def health_check():
    """Verifica se a API esta funcionando."""
    return {"status": "ok"}
