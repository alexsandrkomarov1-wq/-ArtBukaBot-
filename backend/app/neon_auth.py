"""Server-side verification for Neon Managed Auth access tokens.

Neon identities are deliberately not auto-provisioned or linked by email.
A local KOMAROVA_CORE account must be explicitly linked first.
"""
from __future__ import annotations

from functools import lru_cache

import jwt
from jwt import PyJWKClient


@lru_cache(maxsize=4)
def _jwks_client(jwks_url: str) -> PyJWKClient:
    return PyJWKClient(jwks_url, cache_jwk_set=True)


def verify_neon_token(token: str, *, jwks_url: str, issuer: str) -> dict:
    if not jwks_url or not issuer:
        raise ValueError("Neon Auth JWKS URL and issuer are required")
    signing_key = _jwks_client(jwks_url).get_signing_key_from_jwt(token)
    claims = jwt.decode(
        token,
        signing_key.key,
        algorithms=["EdDSA"],
        issuer=issuer,
        options={"require": ["exp", "iss", "sub"], "verify_aud": False},
    )
    if not isinstance(claims.get("sub"), str) or not claims["sub"]:
        raise jwt.InvalidTokenError("Missing Neon subject")
    return claims
