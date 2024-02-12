import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from routes.lamoda_routes import category_router as lamoda_category_router, item_router as lamoda_item_router

app = FastAPI()

app.include_router(
    lamoda_category_router,
    tags=["Lamoda categories"],
    prefix="/api/v1/lamoda-category",
)

app.include_router(
    lamoda_item_router,
    tags=["Lamoda items"],
    prefix="/api/v1/lamoda-items",
)
