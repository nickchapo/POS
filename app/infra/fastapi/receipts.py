from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.infra.core.domain.request.add_receipt_product_request import AddReceiptProductRequest
from app.infra.core.domain.response.receipt_response import ReceiptResponse
from app.infra.core.errors import DoesNotExistError, ExistsError
from app.infra.core.service.receipts import ReceiptService
from app.infra.fastapi.dependables import get_receipt_service

router = APIRouter(prefix="/receipts", tags=["Receipts"])


@router.post("", response_model=ReceiptResponse, status_code=201)
def create_receipt(
        receipt_service: ReceiptService = Depends(get_receipt_service),
) -> ReceiptResponse:
    try:
        response = receipt_service.add_receipt()
    except ExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return response


@router.get("/{receipt_id}", response_model=ReceiptResponse)
def get_receipt(
        receipt_id: UUID,
        receipt_service: ReceiptService = Depends(get_receipt_service),
) -> ReceiptResponse:
    try:
        response = receipt_service.get_receipt(receipt_id)
    except DoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return response


@router.post("/{receipt_id}/products", response_model=ReceiptResponse)
def add_product_to_receipt(
        receipt_id: UUID,
        product_request: AddReceiptProductRequest,
        receipt_service: ReceiptService = Depends(get_receipt_service),
) -> ReceiptResponse:
    try:
        updated_receipt = receipt_service.add_product(receipt_id, product_request.product_id)
    except DoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return updated_receipt
