import uvicorn
from fastapi import FastAPI

from app.infra.fastapi.products import router as product_api
from app.infra.sqlite.products import ProductSQLite

POS_DB = "pos.db"


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(product_api)
    app.state.products = ProductSQLite(POS_DB)
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("pos.main:app", host="127.0.0.1", port=8000, reload=True)
