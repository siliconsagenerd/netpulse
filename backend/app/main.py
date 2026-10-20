from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import get_settings
from .core.database import Base, engine
from .api.routes import router
from .middleware import RequestIdMiddleware, SecurityHeadersMiddleware

settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    if settings.auto_create_tables:
        Base.metadata.create_all(bind=engine)
    from .simulation.engine import ensure_seed_data, recover_stale_runs
    from .core.database import SessionLocal
    db = SessionLocal()
    try:
        ensure_seed_data(db)
        recover_stale_runs(db)
    finally:
        db.close()


app.include_router(router, prefix="/api")
