from fastapi import FastAPI
from .routers import router


def create_app():
    app = FastAPI(
        title="Spimex Trading API",
        version="1.0.0",
        description="API для работы с данными биржевых торгов"
    )
    app.include_router(router=router)
    return app
