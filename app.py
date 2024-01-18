import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from routes.lamoda_routes import category_router as lamoda_category_router

app = FastAPI()

app.include_router(
    lamoda_category_router,
    tags=["Lamoda categories"],
    prefix="/api/v1/lamoda-category",
)
