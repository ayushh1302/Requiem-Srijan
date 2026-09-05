from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.utils.config import APP_NAME, APP_VERSION, HACKATHON_NAME
from backend.storage.database import init_db
from backend.api.routes_health import router as health_router
from backend.api.routes_upload import router as upload_router
from backend.api.routes_analysis import router as analysis_router
from backend.api.routes_chat import router as chat_router
from backend.api.routes_report import router as report_router
from backend.api.routes_reset import router as reset_router

import sys
try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure DB tables exist
    init_db()
    print(f"[STARTUP] {APP_NAME} v{APP_VERSION} Backend Initialized ({HACKATHON_NAME})")
    yield
    # Shutdown
    print(f"[SHUTDOWN] {APP_NAME} Backend Shutdown Cleanly")

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=f"AI-Powered Legal Tech Contract Analyzer for {HACKATHON_NAME}",
    lifespan=lifespan
)

# Enable CORS for Streamlit frontend and local browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pathlib import Path
from fastapi.responses import FileResponse, HTMLResponse

STATIC_DIR = Path(__file__).resolve().parent / "static"

@app.get("/landing", response_class=HTMLResponse)
@app.get("/", response_class=HTMLResponse)
async def serve_landing():
    landing_file = STATIC_DIR / "landing.html"
    if landing_file.exists():
        return FileResponse(str(landing_file), media_type="text/html")
    return HTMLResponse("<h1>Alwayzz Landing Page</h1><p>Please check backend/static/landing.html</p>")

# Register API Routers
app.include_router(health_router)
app.include_router(upload_router)
app.include_router(analysis_router)
app.include_router(chat_router)
app.include_router(report_router)
app.include_router(reset_router)

if __name__ == "__main__":
    import uvicorn
    from backend.utils.config import BACKEND_HOST, BACKEND_PORT
    uvicorn.run("backend.main:app", host=BACKEND_HOST, port=BACKEND_PORT, reload=True)
