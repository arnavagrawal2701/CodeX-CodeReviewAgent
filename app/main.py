# app/main.py
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.graph_routes import router as graph_router
from app.workflows.code_review import register_default_workflow


# -------------------------------
# Create FastAPI App
# -------------------------------
app = FastAPI(
    title="Workflow Engine - Code Review Mini Agent",
    version="1.0.0",
    description="A minimal stateful workflow engine for code quality analysis."
)


# -------------------------------
# Register default workflow on startup
# -------------------------------
@app.on_event("startup")
async def startup_event():
    register_default_workflow()


# -------------------------------
# Serve static frontend files
# -------------------------------
# Mount the /static directory to serve HTML/CSS/JS
app.mount("/static", StaticFiles(directory="static"), name="static")


# -------------------------------
# Landing page redirect
# -------------------------------
@app.get("/", include_in_schema=False)
def landing_redirect():
    """
    Redirect root URL → landing page (static HTML).
    """
    return RedirectResponse(url="/static/landing.html")


# -------------------------------
# Include API routes
# -------------------------------
app.include_router(graph_router, prefix="/graph", tags=["Graph Engine"])


# -------------------------------
# Optional health check
# -------------------------------
@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "message": "Server is running"}
