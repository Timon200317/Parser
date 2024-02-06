import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from common.config import FastAPISettings, get_fastapi_settings, MongoConfig, get_mongo_settings, MongoSettings, \
    get_mongo_config
from routes.lamoda_routes import category_router as lamoda_category_router, item_router as lamoda_item_router

load_dotenv()
app = FastAPI()


@app.get("/")
async def read_root(
        fastapi_settings: FastAPISettings = Depends(get_fastapi_settings),
        database: MongoConfig = Depends(get_mongo_config),
):
    return {"message": "Hello, World!", "fastapi_settings": fastapi_settings.model_dump(),
            "mongo_settings": database.mongo_uri
            }


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
