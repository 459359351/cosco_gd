from fastapi import APIRouter

from app.api.v1.routes import alerts, cargo, data_console, flow, kpi, ranking, repair, sys_dict, throughput, yards

api_router = APIRouter()
api_router.include_router(yards.router, prefix="/yards", tags=["yards"])
api_router.include_router(kpi.router, prefix="/kpi", tags=["kpi"])
api_router.include_router(throughput.router, prefix="/throughput", tags=["throughput"])
api_router.include_router(cargo.router, prefix="/cargo", tags=["cargo"])
api_router.include_router(ranking.router, prefix="/ranking", tags=["ranking"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(flow.router, prefix="/flow", tags=["flow"])
api_router.include_router(data_console.router, prefix="/data-console", tags=["data-console"])
api_router.include_router(sys_dict.router, prefix="/sys-dict", tags=["sys-dict"])
api_router.include_router(repair.router, prefix="/repair", tags=["repair"])
