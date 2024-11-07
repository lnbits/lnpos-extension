from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from lnbits.core.crud import get_user
from lnbits.core.models import WalletTypeInfo
from lnbits.decorators import (
    require_admin_key,
    require_invoice_key,
)

from .crud import (
    create_lnpos,
    delete_lnpos,
    get_lnpos,
    get_lnposs,
    update_lnpos,
)
from .models import CreateLnpos

lnpos_api_router = APIRouter()


@lnpos_api_router.post("/api/v1", dependencies=[Depends(require_admin_key)])
async def api_lnpos_create(data: CreateLnpos):
    return await create_lnpos(data)


@lnpos_api_router.put("/api/v1/{lnpos_id}", dependencies=[Depends(require_admin_key)])
async def api_lnpos_update(data: CreateLnpos, lnpos_id: str):
    lnpos = await get_lnpos(lnpos_id)
    if not lnpos:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="lnpos does not exist"
        )
    for field, value in data.dict().items():
        setattr(lnpos, field, value)
    return await update_lnpos(lnpos)


@lnpos_api_router.get("/api/v1")
async def api_lnposs_get(wallet: WalletTypeInfo = Depends(require_invoice_key)):
    user = await get_user(wallet.wallet.user)
    assert user, "Lnpos cannot retrieve user"
    return await get_lnposs(user.wallet_ids)


@lnpos_api_router.get("/api/v1/{lnpos_id}", dependencies=[Depends(require_invoice_key)])
async def api_lnpos_get(lnpos_id: str):
    lnpos = await get_lnpos(lnpos_id)
    if not lnpos:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="LNPoS does not exist"
        )
    return lnpos


@lnpos_api_router.delete(
    "/api/v1/{lnpos_id}", dependencies=[Depends(require_admin_key)]
)
async def api_lnpos_delete(lnpos_id: str):
    lnpos = await get_lnpos(lnpos_id)
    if not lnpos:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="LNPoS does not exist."
        )

    await delete_lnpos(lnpos_id)
