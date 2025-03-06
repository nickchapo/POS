from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.infra.core.errors import DoesNotExistError, ExistsError
from app.infra.core.repository.receipts import ReceiptEntity, ReceiptRepository
from app.infra.fastapi.dependables import get_receipt_repository

router = APIRouter(prefix="/receipts", tags=["Receipts"])


class ReceiptResponse(BaseModel):
    id: UUID


def _to_response(receipt: ReceiptEntity) -> ReceiptResponse:
    return ReceiptResponse(
        id=receipt.id
    )


@router.post("", response_model=ReceiptResponse, status_code=201)
def create_receipt(
        repo: ReceiptRepository = Depends(get_receipt_repository),
) -> ReceiptResponse:
    receipt = ReceiptEntity()
    try:
        repo.add(receipt)
    except ExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return _to_response(receipt)


@router.get("/{receipt_id}", response_model=ReceiptResponse)
def get_receipt(
        receipt_id: UUID,
        repo: ReceiptRepository = Depends(get_receipt_repository),
) -> ReceiptResponse:
    try:
        receipt = repo.get(receipt_id)
    except DoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _to_response(receipt)
