import uvicorn
from fastapi import FastAPI

from app.infra.fastapi.products import router as product_api
from app.infra.fastapi.shifts import router as shift_api
from app.infra.fastapi.receipts import router as receipt_api
from app.infra.sqlite.products import ProductSQLite
from app.infra.sqlite.receipt_repository import ReceiptSqlLite
from app.infra.sqlite.shifts import ShiftSQLite

POS_DB = "pos.db"


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(product_api)
    app.include_router(shift_api)
    app.include_router(receipt_api)
    app.state.products = ProductSQLite(POS_DB)
    app.state.shifts = ShiftSQLite(POS_DB)
    app.state.receipts = ReceiptSqlLite(POS_DB)
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
