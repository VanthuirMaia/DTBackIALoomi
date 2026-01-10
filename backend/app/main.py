from pathlib import Path
from dotenv import load_dotenv

# Carrega .env antes de qualquer import que use variáveis de ambiente
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

from fastapi import FastAPI

from app.api.routes import paints, chat

app = FastAPI(
    title="Assistente Inteligente de Tintas",
    description="API para recomendação de tintas usando IA",
    version="1.0.0"
)


app.include_router(paints.router)
app.include_router(chat.router)


@app.get("/health", tags=["Health"], summary="Health Check")
def health_check():
    """Verifica se a API está funcionando."""
    return {"status": "ok"}
