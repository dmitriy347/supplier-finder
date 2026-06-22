from fastapi import FastAPI

from api.routers.suppliers import router as suppliers_router

app = FastAPI(title="Supplier Finder API")

app.include_router(suppliers_router)