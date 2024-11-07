import json
from typing import Optional

from lnurl.types import LnurlPayMetadata
from pydantic import BaseModel


class CreateLnpos(BaseModel):
    title: str
    wallet: str
    currency: Optional[str] = "sat"
    profit: Optional[float] = None


class Lnpos(BaseModel):
    id: str
    key: str
    title: str
    wallet: str
    profit: float
    currency: str

    @property
    def lnurlpay_metadata(self) -> LnurlPayMetadata:
        return LnurlPayMetadata(json.dumps([["text/plain", self.title]]))


class LnposPayment(BaseModel):
    id: str
    lnpos_id: str
    payment_hash: str
    payload: str
    pin: int
    sats: int
