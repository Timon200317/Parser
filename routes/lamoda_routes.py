from typing import List

import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException
from models.lamoda_models import CategoryModel
from services.lamoda_db import LamodaServiceDatabase

lamoda_mongo = LamodaServiceDatabase()
category_router = APIRouter()

lamoda_url = f"https://www.lamoda.by/"


# @category_router.get(
#     "/",
#     response_description="List of all the categories",
#     response_model=List[CategoryModel],
# )
# def list_lamoda_categories():
#     categories = lamoda_mongo.list_lamoda_categories()
#     return


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
            product_price = int(product.find('span', class_='x-product-card-description__price').text.strip())
            print(product)
            result.append({
                "brand_name": brand_name,
                "product_name": product_name,
                "product_price": product_price
            })

        return result

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve data from Lamoda: {str(e)}")
