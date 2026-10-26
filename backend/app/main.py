import json
import os
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import init_db

app = FastAPI(
    title="Ralypto Gym API",
    version="1.0.0",
    description="Multi-tenant gym management system API with AI agents, role gating, and offline check-in.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


# Standard Error Format Handler
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        code = exc.detail.get("code", "ERROR")
        message = exc.detail.get("message", "An error occurred")
        details = {k: v for k, v in exc.detail.items() if k not in ["code", "message"]}
    else:
        code = "HTTP_ERROR"
        message = str(exc.detail)
        details = {}

    return JSONResponse(
        status_code=exc.status_code,
        content={"code": code, "message": message, "details": details},
    )


@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs_url": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}


# Include versioned API router
app.include_router(api_router)


def export_openapi():
    """Utility to export the OpenAPI schema to docs/openapi.json."""
    openapi_schema = app.openapi()
    docs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "docs"))
    os.makedirs(docs_path, exist_ok=True)
    out_file = os.path.join(docs_path, "openapi.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2)
    print(f"Exported OpenAPI schema to {out_file}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
