from fastapi import FastAPI

app = FastAPI(
    title="Assistente Inteligente de Tintas",
    description="API para recomendação de tintas usando IA",
    version="1.0.0"
)


@app.get("/health", tags=["Health"], summary="Health Check")
def health_check():
    """Verifica se a API está funcionando."""
    return {"status": "ok"}
