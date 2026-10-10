from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.ppp.routers import registroLogin, RouterSubasta, routerArticulo
from backend.ppp.services.subasta_scheduler import subasta_lifespan


app = FastAPI(
    title="API subasta online",
    description="API de login y gestión de subastas con cierre automático",
    version="1.0.0",
    lifespan=subasta_lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia "*" por las URLs de tu frontend en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(registroLogin.router)
app.include_router(RouterSubasta.router)
app.include_router(routerArticulo.router)

@app.get("/")
def read_root():
    return {"message": "Hola desde el servidor"}