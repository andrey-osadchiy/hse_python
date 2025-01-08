import psycopg2
from faker import Faker
import random
 
# Конфигурация подключения к PostgreSQL
DB_CONFIG = {
    'dbname': 'shop',
    'user': 'airflow',
    'password': 'airflow',
    'host': 'localhost',
    'port': '5433'
}
 
# Создаем соединение с базой данных
conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()
 
# Фейковые данные
fake = Faker()
 
# Генерация данных для Users
def insert_users(num_rows=100):
    users = []
    for _ in range(num_rows):
        users.append(
            (
                fake.first_name(),
                fake.last_name(),
                fake.email(),
                fake.phone_number(),
                fake.date_between(start_date='-10y', end_date='today'),
                random.choice(['Gold', 'Silver', 'Bronze'])
            )
        )
    cursor.executemany(
        "INSERT INTO public.Users (first_name, last_name, email, phone, registration_date, loyalty_status) VALUES (%s, %s, %s, %s, %s, %s)",
        users
    )
 
# Генерация данных для Products
def insert_products(num_rows=100):
    products = []
    for _ in range(num_rows):
        products.append(
            (
                fake.word(),
                fake.text(max_nb_chars=50),
                random.randint(1, 5),
                round(random.uniform(10, 500), 2),
                random.randint(1, 50),
                fake.date_between(start_date='-1y', end_date='today')
            )
        )
    cursor.executemany(
        "INSERT INTO public.Products (name, description, category_id, price, stock_quantity, creation_date) VALUES (%s, %s, %s, %s, %s, %s)",
        products
    )
 
# Генерация данных для Orders
def insert_orders(num_rows=50):
    orders = []
    for _ in range(num_rows):
        orders.append(
            (
                random.randint(1, 100),
                round(random.uniform(50, 1000), 2),
                random.choice(['Pending', 'Completed', 'Cancelled']),
                fake.date_time_this_year(before_now=True, after_now=False)
            )
        )
    cursor.executemany(
        "INSERT INTO public.Orders (user_id, total_amount, status, order_date) VALUES (%s, %s, %s, %s)",
        orders
    )
 
# Генерация данных для OrderDetails
def insert_order_details(num_rows=60):
    order_details = []
    for _ in range(num_rows):
        order_details.append(
            (
                random.randint(1, 100),
                random.randint(1, 100),
                random.randint(1, 10),
                round(random.uniform(5, 100), 2),
                round(random.uniform(5, 1000), 2)
            )
        )
    cursor.executemany(
        "INSERT INTO public.OrderDetails (order_id, product_id, quantity, price_per_unit, total_price) VALUES (%s, %s, %s, %s, %s)",
        order_details
    )
 
# Генерация данных для ProductCategories
def insert_product_categories(num_rows=15):
    categories = []
    for _ in range(num_rows):
        categories.append(
            (
                fake.word(),
                random.randint(1, 5) if _ > 0 else None  # создаем родительскую категорию для некоторых категорий
            )
        )
    cursor.executemany(
        "INSERT INTO public.ProductCategories (name, parent_category_id) VALUES (%s, %s)",
        categories
    )
 
# Вызов функций вставки данных
#insert_users()
insert_products()
insert_product_categories()
#insert_orders()
#insert_order_details()

# Подтверждение изменений
conn.commit()
 
# Закрытие соединения
cursor.close()
conn.close()