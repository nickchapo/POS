from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.domain.request.add_payment_request import AddPaymentRequest
from app.core.domain.request.add_receipt_product_request import (
    AddReceiptProductRequest,
)
from app.core.domain.request.create_receipt_request import CreateReceiptRequest
from app.core.domain.request.quote_request import QuoteRequest
from app.core.domain.response.payment_response import PaymentResponse
from app.core.domain.response.receipt_response import ReceiptResponse
from app.core.errors import DoesNotExistError, ExistsError
from app.core.service.payments import PaymentService
from app.core.service.receipts import ReceiptService
from app.infra.fastapi.dependables import get_payment_service, get_receipt_service

router = APIRouter(prefix="/receipts", tags=["Receipts"])


@router.post("", response_model=ReceiptResponse, status_code=201)
def create_receipt(
        request: CreateReceiptRequest,
        receipt_service: ReceiptService = Depends(get_receipt_service),
) -> ReceiptResponse:
    try:
        response = receipt_service.add_receipt(request.shift_id)
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
        updated_receipt = receipt_service.add_product(
            receipt_id, product_request.product_id
        )
    except DoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return updated_receipt


@router.post("/{receipt_id}/quotes", response_model=PaymentResponse)
def calculate_payment(
        receipt_id: UUID,
        quote_request: QuoteRequest,
        payment_service: PaymentService = Depends(get_payment_service),
) -> PaymentResponse:
    try:
        return payment_service.calculate_total(receipt_id, quote_request.currency)
    except DoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{receipt_id}/payments", response_model=PaymentResponse)
def add_payment(
        receipt_id: UUID,
        payment_request: AddPaymentRequest,
        payment_service: PaymentService = Depends(get_payment_service),
) -> PaymentResponse:
    try:
        return payment_service.add_payment_to_receipt(receipt_id, payment_request)
    except DoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
