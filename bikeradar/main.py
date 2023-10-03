from fastapi import FastAPI


def run():
    app = FastAPI()

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    return app
