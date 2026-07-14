from fastapi import FastAPI
import logging

from .routers import router


logger = logging.getLogger(__name__)


def create_app(lifespan=None):
    app = FastAPI(
        title="Spimex Trading API",
        version="1.0.0",
        description="API для работы с данными биржевых торгов",
        lifespan=lifespan
    )
    app.include_router(router=router)
    return app
