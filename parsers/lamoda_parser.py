import aiohttp
from bs4 import BeautifulSoup
from fastapi import HTTPException

from services.lamoda_db import LamodaServiceDatabase

lamoda_mongo = LamodaServiceDatabase()

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
]


async def get_lamoda_subcategories(url_main_category: str, session):
    response = await session.get(url=lamoda_url + url_main_category)
    soup = BeautifulSoup(await response.text(), "lxml")
    subcategories = soup.find_all('ul', class_="x-tree-view-catalog-navigation__subtree")
    result_list = []
    for subcategory in subcategories:
        subcategories_a = subcategory.find_all('a', class_="x-link x-link__label")
        for subcategory_a in subcategories_a:
            result_list.append(subcategory_a.text.strip())
    return result_list


async def get_urls_categories(session):
    list_urls = []
    for link in links:
        response = await session.get(url=link["url"])
        soup = BeautifulSoup(await response.text(), "lxml")
        major_categories = soup.find('nav').find_all("a")

        for category in major_categories:
            list_urls.append(lamoda_url + category["href"])

    return list_urls
