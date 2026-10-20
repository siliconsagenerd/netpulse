import hashlib
import os
import secrets
from datetime import datetime

from fastapi import Request, Response
from sqlalchemy.orm import Session

from ..core.config import get_settings
from ..models import Workspace

COOKIE_NAME = "np_session"
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() in ("1", "true", "yes")


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def get_workspace(request: Request, response: Response, db: Session) -> Workspace:
    token = request.cookies.get(COOKIE_NAME)
    ws = None
    if token:
        ws = db.query(Workspace).filter(Workspace.token_hash == _hash(token)).first()
    if ws is None:
        token = secrets.token_urlsafe(32)
        ws = Workspace(token_hash=_hash(token))
        db.add(ws)
        db.commit()
        db.refresh(ws)
        from ..simulation.engine import seed_default_rules
        seed_default_rules(db, ws.id)
    else:
        ws.last_seen_at = datetime.utcnow()
        db.commit()
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/",
        max_age=60 * 60 * 24 * 30,
    )
    return ws
