from fastapi import Depends, Request, Response
from sqlalchemy.orm import Session
from .database import get_db
from .session import get_workspace
from ..models import Workspace


def current_workspace(request: Request, response: Response, db: Session = Depends(get_db)) -> Workspace:
    return get_workspace(request, response, db)
