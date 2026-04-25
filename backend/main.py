from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Cognitive Debugging — Agentic Journal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "tauri://localhost"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


# Routers are attached here as worktrees land them. Keep this file thin.
# from api.ingest import router as ingest_router; app.include_router(ingest_router)
# from api.detect import router as detect_router; app.include_router(detect_router)
# from api.persona import router as persona_router; app.include_router(persona_router)
