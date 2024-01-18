from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

# Выбираем базу данных
db = client["your_database"]

# Выбираем коллекцию
collection = db["your_collection"]

# Создаем экземпляр CategoryModel
category_data = CategoryModel(
    category_name="SomeCategory",
    subcategory_name="SomeSubcategory",
    link="https://example.com",
    gender="Male"
)