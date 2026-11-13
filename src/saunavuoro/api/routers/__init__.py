"""Aggregates all API routers."""

from fastapi import APIRouter

from saunavuoro.api.routers import apartments, residents, saunas

api_router = APIRouter()
api_router.include_router(apartments.router)
api_router.include_router(residents.router)
api_router.include_router(saunas.router)
