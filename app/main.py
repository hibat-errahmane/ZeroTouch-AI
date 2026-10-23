from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.config import ROOT, Settings
from app.database import initialize
from app.api.routes import router

PAGES = {"dashboard": ("Dashboard", 1), "teach": ("Teach", 2),
         "workflows": ("Workflows", 3), "run": ("Run", 4), "results": ("Results", 5)}

def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings()
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        (config.data_dir / "uploads").mkdir(parents=True, exist_ok=True)
        initialize(application.state.db_path)
        yield
    application = FastAPI(title="ZeroTouch AI", version="0.1.0", lifespan=lifespan)
    application.state.settings = config
    application.state.db_path = config.data_dir / "zerotouch.sqlite3"
    application.include_router(router)
    application.mount("/static", StaticFiles(directory=ROOT / "app/static"), name="static")
    templates = Jinja2Templates(directory=ROOT / "app/templates")
    @application.get("/", response_class=HTMLResponse)
    async def dashboard(request: Request):
        return templates.TemplateResponse(request=request, name="page.html", context={"page": "dashboard", "pages": PAGES})
    @application.get("/{page}", response_class=HTMLResponse)
    async def page_view(page: str, request: Request):
        if page not in PAGES:
            from fastapi import HTTPException
            raise HTTPException(404, "Page not found")
        return templates.TemplateResponse(request=request, name="page.html", context={"page": page, "pages": PAGES})
    return application

app = create_app()
