import base64
import hmac
from io import BytesIO
from typing import Optional

from embit import compact
from lnbits.helpers import urlsafe_short_hash
from lnbits.utils.exchange_rates import fiat_amount_as_satoshis

from .crud import create_lnpos_payment, get_recent_lnpos_payment
from .models import Lnpos, LnposPayment


async def register_atm_payment(
    device: Lnpos, payload: str
) -> tuple[Optional[LnposPayment], Optional[int]]:
    """
    Register an ATM payment to avoid double pull.
    """
    # create a new lnurlpayment record
    data = base64.urlsafe_b64decode(payload)
    payload = payload.replace("=", "")
    decrypted = xor_decrypt(device.key.encode(), data)

    lnpos_payment = await get_recent_lnpos_payment(payload)
    # If the payment is already registered and been paid, return None
    if lnpos_payment and lnpos_payment.payload == lnpos_payment.payment_hash:
        return None, lnpos_payment.sats * 1000
    # If the payment is already registered and not been paid, return lnurlpayment record
    if lnpos_payment and lnpos_payment.payload != lnpos_payment.payment_hash:
        return lnpos_payment, lnpos_payment.sats * 1000

    price_msat = (
        await fiat_amount_as_satoshis(float(decrypted[1]) / 100, device.currency) * 1000
        if device.currency != "sat"
        else decrypted[1] * 1000
    )
    price_msat = int(price_msat - ((price_msat / 100) * device.profit))
    sats = int(price_msat / 1000)
    lnpos_payment = LnposPayment(
        id=urlsafe_short_hash(),
        lnpos_id=device.id,
        payload=payload,
        sats=sats,
        pin=int(decrypted[0]),
        payment_hash="payment_hash",
    )
    lnpos_payment = await create_lnpos_payment(lnpos_payment)
    price_msat = sats * 1000
    return lnpos_payment, price_msat


def xor_decrypt(key, blob):
    s = BytesIO(blob)
    variant = s.read(1)[0]
    if variant != 1:
        raise RuntimeError("Not implemented")
    # reading nonce
    nonce_len = s.read(1)[0]
    nonce = s.read(nonce_len)
    if len(nonce) != nonce_len:
        raise RuntimeError("Missing nonce bytes")
    if nonce_len < 8:
        raise RuntimeError("Nonce is too short")

    # reading payload
    payload_len = s.read(1)[0]
    payload = s.read(payload_len)
    if len(payload) > 32:
        raise RuntimeError("Payload is too long for this encryption method")
    if len(payload) != payload_len:
        raise RuntimeError("Missing payload bytes")
    hmacval = s.read()
    expected = hmac.new(
        key, b"Data:" + blob[: -len(hmacval)], digestmod="sha256"
    ).digest()
    if len(hmacval) < 8:
        raise RuntimeError("HMAC is too short")
    if hmacval != expected[: len(hmacval)]:
        raise RuntimeError("HMAC is invalid")
    secret = hmac.new(key, b"Round secret:" + nonce, digestmod="sha256").digest()
    payload = bytearray(payload)
    for i in range(len(payload)):
        payload[i] = payload[i] ^ secret[i]
    s = BytesIO(payload)
    pin = compact.read_from(s)
    amount_in_cent = compact.read_from(s)
    return str(pin), amount_in_cent
