from pathlib import Path

# Aktifkan truststore agar menggunakan certificate store sistem Windows
try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.routes import router

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"

app = FastAPI(
    title="OpsPilot AI",
    description="Technical Support and Troubleshooting Assistant",
    version="0.1.0",
)

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

app.include_router(router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"title": "OpsPilot AI"},
    )
