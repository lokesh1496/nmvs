import asyncio
from contextlib import asynccontextmanager
from database.database import Base, engine
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
from app.config import settings
from app.monitoring.model import MonitoringHistory
from app.speed_monitoring.model import DeviceBandwidthHistory
from app.users.model import User
from app.alerts.model import Alert
from app.devices.router import router as devices_router
from app.discovery.router import router as discovery_router
from app.monitoring.router import router as monitoring_router
from app.speed_monitoring.router import router as speed_monitoring_router
from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.topology.router import router as topology_router
from app.dashboard.router import router as dashboard_router
from app.alerts.router import router as alerts_router
from app.reports.router import router as reports_router
from app.metrics.router import router as metrics_router
from app.monitoring.scheduler import monitor_devices

# Apply any pending Alembic migrations
try:
    import os
    from alembic import command
    from alembic.config import Config

    alembic_ini_path = os.path.join(os.path.dirname(__file__), "alembic.ini")
    if os.path.exists(alembic_ini_path):
        alembic_cfg = Config(alembic_ini_path)
        command.upgrade(alembic_cfg, "head")
except Exception as e:
    print(f"Alembic migration notice: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):

    monitoring_task = asyncio.create_task(
        monitor_devices(settings.DEVICE_MONITOR_INTERVAL)
    )

    yield

    monitoring_task.cancel()

    try:
        await monitoring_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Network Monitoring and Visualization System",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "*",
    ],
    allow_origin_regex=r".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(devices_router)
app.include_router(discovery_router)
app.include_router(monitoring_router)
app.include_router(speed_monitoring_router)
app.include_router(topology_router)
app.include_router(dashboard_router)
app.include_router(alerts_router)
app.include_router(reports_router)
app.include_router(metrics_router)


FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "stitch_nmvs_network_visibility_dashboard")
)

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/api.js", include_in_schema=False)
    def serve_api_js():
        return FileResponse(os.path.join(FRONTEND_DIR, "api.js"), media_type="application/javascript")

    @app.get("/ui", include_in_schema=False)
    @app.get("/dashboard-view", include_in_schema=False)
    def ui_dashboard():
        html_path = os.path.join(FRONTEND_DIR, "nmvs_network_visibility_monitoring_dashboard", "code.html")
        return FileResponse(html_path)

    @app.get("/devices-view", include_in_schema=False)
    def ui_devices():
        html_path = os.path.join(FRONTEND_DIR, "nmvs_device_management_fleet_inventory", "code.html")
        return FileResponse(html_path)

    @app.get("/devices-inventory-view", include_in_schema=False)
    def ui_devices_inventory():
        html_path = os.path.join(FRONTEND_DIR, "nmvs_device_management_inventory", "code.html")
        return FileResponse(html_path)

    @app.get("/topology-view", include_in_schema=False)
    def ui_topology():
        html_path = os.path.join(FRONTEND_DIR, "nmvs_interactive_network_topology", "code.html")
        return FileResponse(html_path)

    @app.get("/speed-monitoring-view", include_in_schema=False)
    def ui_speed():
        html_path = os.path.join(FRONTEND_DIR, "nmvs_speed_monitoring_historical_telemetry_probe_1", "code.html")
        return FileResponse(html_path)

    @app.get("/speed-monitoring-probe2-view", include_in_schema=False)
    def ui_speed_probe2():
        html_path = os.path.join(FRONTEND_DIR, "nmvs_speed_monitoring_historical_telemetry_probe_2", "code.html")
        return FileResponse(html_path)

    @app.get("/login", include_in_schema=False)
    @app.get("/login-view", include_in_schema=False)
    def ui_login():
        html_path = os.path.join(FRONTEND_DIR, "login.html")
        return FileResponse(html_path)


@app.get("/")
def home(request: Request):
    accept = request.headers.get("accept", "")
    if "text/html" in accept and os.path.exists(FRONTEND_DIR):
        dashboard_html = os.path.join(FRONTEND_DIR, "nmvs_network_visibility_monitoring_dashboard", "code.html")
        if os.path.exists(dashboard_html):
            return FileResponse(dashboard_html)
    return {
        "message": "NMVS API is running",
        "service": "Network Monitoring and Visualization System",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "ui": "/ui"
    }


@app.get("/health")
def health():
    from database.database import get_db_stats
    db_stats = get_db_stats()
    return {
        "status": "healthy",
        "service": "Network Monitoring and Visualization System API",
        "version": "1.0.0",
        "database": db_stats
    }
