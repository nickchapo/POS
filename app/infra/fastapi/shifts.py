from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.infra.core.errors import DoesNotExistError, ShiftClosedError
from app.infra.core.repository.shifts import ShiftRepository
from app.infra.fastapi.dependables import get_shift_repository

router = APIRouter(prefix="/shifts", tags=["Shifts"])


class ShiftResponse(BaseModel):
    id: UUID
    open_at: datetime
    closed_at: Optional[datetime] = None


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
