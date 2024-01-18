import aiohttp
from bs4 import BeautifulSoup

from services.lamoda_db import LamodaServiceDatabase

lamoda_mongo = LamodaServiceDatabase()

base_url = "https://www.lamoda.by"
links = [
    {
        "gender": "Женщинам",
        "url": "https://www.lamoda.by/c/4153/default-women/?is_new=1&sitelink=topmenuW&l=1",
    },
    {
        "gender": "Мужчинам",
        "url": "https://www.lamoda.by/c/4152/default-men/?is_new=1&sitelink=topmenuM&l=1",
    },
]


async def get_lamoda_categories():
    for link in links:
        async with aiohttp.ClientSession as session:
            response = await session.get(url=link["url"])
            soup = BeautifulSoup(await response.text(), "lxml")
            major_categories = soup.find_all('')


async def get_lamoda_categories_to_insert_in_mongo():
    """Main function for transform data from parse to mongo db"""
    list_categories = await get_lamoda_categories()
    await lamoda_mongo.parse_lamoda_categories(list_categories)
