from __future__ import annotations

from datetime import datetime, timedelta, timezone
import uuid

import jwt
from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_SECONDS = 30 * 60


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password, password_hash)
    except Exception:
        return False


def create_access_token(user_id: str, secret: str) -> tuple[str, str, datetime]:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(seconds=ACCESS_TOKEN_SECONDS)
    token_id = str(uuid.uuid4())
    token = jwt.encode(
        {"sub": user_id, "jti": token_id, "iat": now, "exp": expires_at},
        secret,
        algorithm=JWT_ALGORITHM,
    )
    return token, token_id, expires_at


def decode_access_token(token: str, secret: str) -> dict:
    return jwt.decode(token, secret, algorithms=[JWT_ALGORITHM], options={"require": ["sub", "jti", "exp"]})
