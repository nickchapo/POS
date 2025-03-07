from collections import defaultdict
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.domain.response.shift_report_response import ShiftReportResponse
from app.core.domain.response.shift_response import ShiftResponse
from app.core.errors import DoesNotExistError, ShiftClosedError
from app.core.repository.receipts import Receipt, ReceiptRepository
from app.core.repository.shifts import ShiftRepository
from app.core.service.payments import PaymentService
from app.infra.fastapi.dependables import (
    get_payment_service,
    get_receipt_repository,
    get_shift_repository,
)

router = APIRouter(prefix="/shifts", tags=["Shifts"])


def calculate_shift_report(shift_id: UUID,
                           receipts: List[Receipt]) -> ShiftReportResponse:
    total_receipts = len(receipts)
    items_sold = defaultdict(int)
    total_revenue_gel = 0.0

    for receipt in receipts:
        for product in receipt.products:
            items_sold[str(product.id)] += 1
            total_revenue_gel += product.price

    return ShiftReportResponse(
        shift_id=str(shift_id),
        receipts_count=total_receipts,
        items_sold=dict(items_sold),
        revenue={"GEL": total_revenue_gel}
    )


@router.get("/x-reports", response_model=ShiftReportResponse)
def get_x_report(
        shift_id: UUID,
        shift_repo: ShiftRepository = Depends(get_shift_repository),
        receipt_repo: ReceiptRepository = Depends(get_receipt_repository)
) -> ShiftReportResponse:
    try:
        shift = shift_repo.read(shift_id)
    except DoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if getattr(shift, "closed", False):
        raise HTTPException(status_code=400, detail="Shift is already closed")

    receipts = receipt_repo.get_by_shift(shift_id)
    return calculate_shift_report(shift_id, receipts)


@router.get("/y-reports", response_model=ShiftReportResponse)
def get_y_report(
        shift_id: UUID,
        shift_repo: ShiftRepository = Depends(get_shift_repository),
        receipt_repo: ReceiptRepository = Depends(get_receipt_repository),
        payment_service: PaymentService = Depends(get_payment_service)
) -> ShiftReportResponse:
    try:
        shift = shift_repo.read(shift_id)
    except DoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e))

    receipts = receipt_repo.get_by_shift(shift_id)

    for receipt in receipts:
        if not payment_service.has_payment_to_receipt(receipt.id):
            raise HTTPException(
                status_code=400,
                detail=f"Receipt {receipt.id} is unpaid; cannot close shift."
            )

    if not getattr(shift, "closed", False):
        try:
            shift_repo.close_shift(shift_id)
        except (DoesNotExistError, ShiftClosedError) as e:
            raise HTTPException(status_code=400, detail=str(e))
        shift = shift_repo.read(shift_id)

    return calculate_shift_report(shift_id, receipts)


@router.post("", response_model=ShiftResponse, status_code=201)
def open_shift(repo: ShiftRepository = Depends(get_shift_repository)) -> ShiftResponse:
    shift = repo.open_shift()
    return ShiftResponse(**shift.__dict__)


@router.patch("/{shift_id}/close", response_model=ShiftResponse)
def close_shift(
        shift_id: UUID, repo: ShiftRepository = Depends(get_shift_repository)
) -> ShiftResponse:
    try:
        repo.close_shift(shift_id)
    except DoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ShiftClosedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    shift = repo.read(shift_id)
    return ShiftResponse(**shift.__dict__)


@router.get("/{shift_id}", response_model=ShiftResponse)
def get_shift(
        shift_id: UUID, repo: ShiftRepository = Depends(get_shift_repository)
) -> ShiftResponse:
    try:
        shift = repo.read(shift_id)
    except DoesNotExistError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ShiftResponse(**shift.__dict__)
