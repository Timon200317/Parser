from typing import List

import aiohttp
import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException
from models.lamoda_models import CategoryModel
from services.lamoda_db import LamodaServiceDatabase

lamoda_mongo = LamodaServiceDatabase()
category_router = APIRouter()

lamoda_url = "https://www.lamoda.by"

lamoda_mongo = LamodaServiceDatabase()

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


@category_router.get("api/v1/lamoda-major-categories/")
async def get_lamoda_categories():
    try:
        result = []
        for link in links:
            result_link = link["gender"]
            async with aiohttp.ClientSession() as session:
                response = await session.get(url=link["url"])
                soup = BeautifulSoup(await response.text(), "lxml")
                major_categories = soup.find('nav').find_all("a")
                list_categories = []
                for category in major_categories:
                    subcategories = await get_lamoda_subcategories(category["href"], session)
                    list_categories.append({
                        "category_name": category.text.strip(),
                        "href": lamoda_url+category["href"],
                        "subcategory": subcategories
                    })
                    CategoryModel(
                        category_name=category.text.strip(),
                        subcategory_name=subcategories,
                        gender=link["gender"],
                        link=lamoda_url+category["href"],
                    )
                result.append({
                    "gender": result_link,
                    "categories": list_categories,
                })
        return result

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve data from Lamoda: {str(e)}")


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


async def get_lamoda_categories_to_insert_in_mongo():
    """Main function for transform data from parse to mongo db"""
    list_categories = await get_lamoda_categories()
    await lamoda_mongo.parse_lamoda_categories(list_categories)


@category_router.get("api/v1/lamoda-subcategories/")
async def get_item_info():
    try:
        # Отправляем GET-запрос к странице категории
        response = requests.get(lamoda_url)
        response.raise_for_status()  # Проверяем успешность запроса

        # Создаем объект BeautifulSoup для парсинга HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        subcategories = soup.select(
            "div[class=x-tree-view-catalog-navigation__category]",
        )

        print(subcategories)

        if subcategories:
            # Получаем текст из элемента и разделяем его на список категорий

            return subcategories

        else:
            return []

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve data from Lamoda: {str(e)}")


@category_router.get("/api/v1/lamoda-categories/")
async def get_all_categories():
    lamoda_url = f"https://www.lamoda.by/"

    try:
        # Отправляем GET-запрос к странице категории
        response = requests.get(lamoda_url)
        response.raise_for_status()  # Проверяем успешность запроса

        # Создаем объект BeautifulSoup для парсинга HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        categories_element = soup.select_one('nav')

        print(categories_element)

        if categories_element:
            # Получаем текст из элемента и разделяем его на список категорий
            categories_list = [category.strip() for category in categories_element.stripped_strings]

            return categories_list

        else:
            return []

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve data from Lamoda: {str(e)}")


@category_router.get("/lamoda-products/{category}")
async def get_lamoda_products(category: str, index: int):
    lamoda_url = f"https://www.lamoda.by/c/{index}/{category}/"

    try:
        # Отправляем GET-запрос к странице категории
        response = requests.get(lamoda_url)
        response.raise_for_status()  # Проверяем успешность запроса

        # Создаем объект BeautifulSoup для парсинга HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Находим все товары на странице

        # Собираем информацию о товарах
        result = []
        products = soup.find_all('div', class_="x-product-card-description")
        for product in products:
            brand_name = product.find('div', class_='x-product-card-description__brand-name').text.strip()
            product_name = product.find('div', class_='x-product-card-description__product-name').text.strip()
            print(product)
            result.append({
                "brand_name": brand_name,
                "product_name": product_name,
            })

        return result

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve data from Lamoda: {str(e)}")
