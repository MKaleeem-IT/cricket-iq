from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from auth import router as auth_router
from predict_api import router as predict_router
from upcoming_api import router as upcoming_router

app = FastAPI(title="Cricket IQ API", version="1.0.0")

# CORS — frontend se requests allow karne ke liye
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(predict_router, prefix="/api", tags=["Predict"])
app.include_router(upcoming_router, prefix="/api", tags=["Upcoming"])

# Serve frontend
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")

    @app.get("/")
    def serve_index():
        return FileResponse(FRONTEND_DIR / "index.html")

    @app.get("/{page}.html")
    def serve_page(page: str):
        file_path = FRONTEND_DIR / f"{page}.html"
        if file_path.exists():
            return FileResponse(file_path)
        return {"error": "Page not found"}


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Cricket IQ API"}