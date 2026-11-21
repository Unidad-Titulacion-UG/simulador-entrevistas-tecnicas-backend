from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from app.api.router import router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url=None,
    redoc_url=None,
)

app.include_router(router)

@app.get("/docs", include_in_schema=False)
def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=f"{settings.APP_NAME} - Documentación de la API",
    )
