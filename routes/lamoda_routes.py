import asyncio
import logging
from decimal import Decimal
from typing import List

import aiohttp
from bs4 import BeautifulSoup
from bson import Decimal128
from fastapi import APIRouter, HTTPException
import logging

from models.lamoda_models import CategoryModel, ItemModel
from parsers.lamoda_parser import get_lamoda_subcategories, get_urls_categories, fetch_category_items
from services.lamoda_db import LamodaServiceDatabase

logger = logging.getLogger(__name__)
lamoda_mongo = LamodaServiceDatabase()
category_router = APIRouter()
item_router = APIRouter()

lamoda_url = "https://www.lamoda.by"

links = [
    {
        "gender": "Женщинам",
        "url": "https://www.lamoda.by/c/4153/default-women/?is_new=1&sitelink=topmenuW&l=1",
    },
    {
        "gender": "Мужчинам",
        "url": "https://www.lamoda.by/c/4152/default-men/?is_new=1&sitelink=topmenuM&l=1",
    },
    {
        "gender": "Детям",
        "url": "https://www.lamoda.by/c/4154/default-kids/?genders=boys%2Cgirls&is_new=1&sitelink=topmenuK&l=2",
    },
]


@category_router.get("/parse_categories")
async def get_lamoda_categories():
    try:
        final_categories_for_mongo = []
        result = []
        connector = aiohttp.TCPConnector(force_close=True)
        timeout = aiohttp.ClientTimeout(total=9000)

        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            tasks = []

            for link in links:
                result_link = link["gender"]
                response = await session.get(url=link["url"])
                soup = BeautifulSoup(await response.text(), "lxml")
                major_categories = soup.find('nav').find_all("a")
                list_categories = []

                for category in major_categories:
                    subcategories = await get_lamoda_subcategories(category["href"], session)
                    list_categories.append({
                        "category_name": category.text.strip(),
                        "link": lamoda_url + category["href"],
                        "subcategory": subcategories
                    })

                    final_categories_for_mongo.append(CategoryModel(
                        category_name=category.text.strip(),
                        subcategory_name=subcategories,
                        gender=link["gender"],
                        link=lamoda_url + category["href"],
                    ))

                tasks.append(lamoda_mongo.parse_lamoda_categories(final_categories_for_mongo))
                result.append({
                    "gender": result_link,
                    "categories": list_categories,
                })

            # Ждем завершения всех параллельных задач
            await asyncio.gather(*tasks)

        return result

    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve data from Lamoda: {str(e)}")


@item_router.get("/parse_items")
async def get_lamoda_items():
    items = []
    connector = aiohttp.TCPConnector(force_close=True)
    timeout = aiohttp.ClientTimeout(total=9000)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = []

        urls = "https://www.lamoda.by/c/355/clothes-zhenskaya-odezhda/?l=2&sitelink=topmenuW"
        logger.info(f"Urls: {urls}")

        # if not urls:
        #     await get_lamoda_categories()
        items += await fetch_category_items(urls, session)
        tasks.append(lamoda_mongo.parse_lamoda_items(items))

        # Ждем завершения всех параллельных задач
        await asyncio.gather(*tasks)
    return items


@category_router.get(
    "/",
    response_description="List of all the categories in mongo",
    response_model=List[CategoryModel],
)
def list_lamoda_categories():
    categories = lamoda_mongo.list_lamoda_categories()
    return categories


@item_router.get(
    "/",
    response_description="List of all the items in mongo",
    response_model=List[ItemModel],
)
def list_lamoda_items():
    items = lamoda_mongo.list_lamoda_items()
    return items
