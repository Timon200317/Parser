import logging
from decimal import Decimal
from models.lamoda_models import (
    CategoryModel,
    ItemModel, UpdateCategoryModel, UpdateItemModel,
)
import aiohttp
from bs4 import BeautifulSoup
from bson import Decimal128
from fastapi import HTTPException

from services.lamoda_db import LamodaServiceDatabase
logger = logging.getLogger(__name__)
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


async def fetch_item(url, session):
    async with session.get(url, headers=None) as response:
        soup = BeautifulSoup(await response.text(), "lxml")

        color = str()
        product_info = soup.findAll("script")[6].text.strip()
        color_index = soup.findAll("script")[6].text.strip().find("Цвет")
        if color_index == -1:
            color = "Не указан"
        else:
            color_index += 15

            while product_info[color_index] != '"':
                color += product_info[color_index]
                color_index += 1

        category = soup.findAll("a", class_="x-link x-link__secondaryLabel")[
            2
        ]
        brand = soup.find(
            "span", class_="x-premium-product-title__brand-name"
        ).text.strip()
        name = soup.find(
            "div", class_="x-premium-product-title__model-name"
        ).text.strip()
        if soup.find("span", class_="x-premium-product-prices__price") is None:
            return None
        price_split = soup.find(
            "span", class_="x-premium-product-prices__price"
        ).text.split(" ")
        price = (
            "".join(price_split[:-1])
            if price_split[-1] == "р."
            else "".join(price_split)
        )
        info_value = soup.findAll(
            "span", class_="x-premium-product-description-attribute__value"
        )
        info_name = soup.findAll(
            "span", class_="x-premium-product-description-attribute__name"
        )
        info_result = {}

        for i, d in zip(info_value, info_name):
            info_result[d.text] = i.text
        article = info_result["Артикул"]

        item = ItemModel(
            name=name,
            article=article,
            category=category.text.strip(),
            price=Decimal128(Decimal(price)),
            brand=brand,
            color=color.capitalize(),
        )
        logger.info(f"Item info: {item}")

        return item


async def fetch_category_items(category_url, client):
    items = []
    async with client.get(category_url, headers=None) as response:
        soup = BeautifulSoup(await response.text(), "lxml")

        items_url = soup.findAll(
            "a", class_="x-product-card__link x-product-card__hit-area"
        )

        for item_url in items_url:
            fetch_items = await fetch_item(lamoda_url + item_url["href"], client)
            if fetch_items is not None:
                items.append(fetch_items)

        return items


# parse lamoda categories and insert in mongo
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

async def get_lamoda_items():
    items = []
    connector = aiohttp.TCPConnector(force_close=True)
    timeout = aiohttp.ClientTimeout(total=9000)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = []

        urls = "https://www.lamoda.by/c/355/clothes-zhenskaya-odezhda/?l=2&sitelink=topmenuW"
        logger.info(f"Urls: {urls}")

        items += await fetch_category_items(urls, session)
        tasks.append(lamoda_mongo.parse_lamoda_items(items))

        # Ждем завершения всех параллельных задач
        await asyncio.gather(*tasks)
    return items
