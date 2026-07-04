from fastapi import FastAPI


def create_app():
    app = FastAPI(
        title="Spimex Trading API",
        version="1.0.0",
        description="API для работы с данными биржевых торгов"
    )

    return app