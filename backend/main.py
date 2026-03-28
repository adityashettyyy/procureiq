from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.config import get_settings
from core.database import init_db
from routers import quotes, suppliers, metrics

settings = get_settings()

print(f"✅ CORS Origins: {settings.cors_origins_list}")
print(f"✅ Demo Mode: {settings.demo_mode}")
print(f"✅ Database: {settings.database_url}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting ProcureIQ backend...")
    await init_db()
    # Seed default suppliers on first run
    from seed import seed_suppliers
    await seed_suppliers()
    print("✅ Database initialized and seeded")
    yield


app = FastAPI(
    title="ProcureIQ API",
    description="Autonomous multi-vendor quote collection powered by TinyFish",
    version=settings.app_version,
    lifespan=lifespan,
)

# ✅ Add CORS middleware BEFORE including routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("✅ CORS middleware configured")

app.include_router(quotes.router)
app.include_router(suppliers.router)
app.include_router(metrics.router)

print("✅ All routers included")


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.app_version, "db": "connected"}


@app.options("/{full_path:path}")
async def preflight_handler(full_path: str):
    """Handle CORS preflight requests"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Starting uvicorn on 0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
