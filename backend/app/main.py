from pathlib import Path
from dotenv import load_dotenv

# Carrega .env antes de qualquer import que use variaveis de ambiente
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from app.api.routes import paints, chat, auth
from app.db.base import Base
from app.db.session import engine

from app.models.paint import Paint  # noqa: F401
from app.models.user import User  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Assistente Inteligente de Tintas",
    description="API para recomendacao de tintas usando IA com autenticacao JWT",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(paints.router)
app.include_router(chat.router)

# Serve frontend estático
frontend_path = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/css", StaticFiles(directory=str(frontend_path / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(frontend_path / "js")), name="js")

    @app.get("/", include_in_schema=False)
    def serve_frontend():
        return FileResponse(str(frontend_path / "index.html"))


@app.get("/health", tags=["Health"], summary="Health Check")
def health_check():
    return {"status": "ok"}