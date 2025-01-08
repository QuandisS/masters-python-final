import os
from faker import Faker
import psycopg2
from psycopg2 import sql
import random
from datetime import datetime, timedelta

# Configuration variables from environment variables
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

# Number of records to generate from environment variables
NUM_USERS = int(os.getenv('NUM_USERS', 100))
NUM_PRODUCTS = int(os.getenv('NUM_PRODUCTS', 100))
NUM_ORDERS = int(os.getenv('NUM_ORDERS', 100))
NUM_ORDER_DETAILS = int(os.getenv('NUM_ORDER_DETAILS', 300))
NUM_CATEGORIES = int(os.getenv('NUM_CATEGORIES', 10))

# Initialize Faker and database connection
fake = Faker()
conn = psycopg2.connect(
    dbname=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cursor = conn.cursor()

# Function to generate unique users
def generate_users(num_users):
    loyalty_statuses = ['Gold', 'Silver', 'Bronze']
    
    for _ in range(num_users):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.unique.email()  # Ensures unique emails
        phone = fake.phone_number()
        registration_date = fake.date_time_this_decade()
        loyalty_status = random.choice(loyalty_statuses)

        cursor.execute(
            sql.SQL("INSERT INTO Users (first_name, last_name, email, phone, registration_date, loyalty_status) VALUES (%s, %s, %s, %s, %s, %s)"),
            (first_name, last_name, email, phone, registration_date, loyalty_status)
        )

# Function to generate products
def generate_products(num_products):
    for _ in range(num_products):
        name = fake.word().capitalize()
        description = fake.text(max_nb_chars=200)
        category_id = random.randint(1, NUM_CATEGORIES)  # Assuming categories from 1 to NUM_CATEGORIES
        price = round(random.uniform(5.0, 500.0), 2)
        stock_quantity = random.randint(1, 1000)
        creation_date = fake.date_time_this_decade()

        cursor.execute(
            sql.SQL("INSERT INTO Products (name, description, category_id, price, stock_quantity, creation_date) VALUES (%s, %s, %s, %s, %s, %s)"),
            (name, description, category_id, price, stock_quantity, creation_date)
        )

# Function to generate orders
def generate_orders(num_orders):
    for _ in range(num_orders):
        user_id = fake.random_element(elements=[fake.unique.email() for _ in range(NUM_USERS)])  # Assuming we have NUM_USERS users
        order_date = fake.date_time_this_year()
        total_amount = round(random.uniform(20.0, 1000.0), 2)
        status = random.choice(['Pending', 'Completed'])
        delivery_date = order_date + timedelta(days=random.randint(1, 10))

        cursor.execute(
            sql.SQL("INSERT INTO Orders (user_id, order_date, total_amount, status, delivery_date) VALUES (%s, %s, %s, %s, %s)"),
            (user_id, order_date, total_amount, status, delivery_date)
        )

# Function to generate order details
def generate_order_details(num_order_details):
    for _ in range(num_order_details):
        order_id = fake.random_element(elements=[fake.uuid4() for _ in range(NUM_ORDERS)])  # Assuming we have NUM_ORDERS orders
        product_id = fake.random_element(elements=[fake.uuid4() for _ in range(NUM_PRODUCTS)])  # Assuming we have NUM_PRODUCTS products
        quantity = random.randint(1, 10)
        
        # Fetching price per unit from Products table (for simplicity we assume it exists)
        cursor.execute(sql.SQL("SELECT price FROM Products WHERE product_id=%s"), [product_id])
        price_per_unit = cursor.fetchone()[0]
        
        total_price = quantity * price_per_unit

        cursor.execute(
            sql.SQL("INSERT INTO OrderDetails (order_id, product_id, quantity, price_per_unit,total_price) VALUES (%s,%s,%s,%s,%s)"),
            (order_id , product_id , quantity , price_per_unit , total_price )
        )

# Function to generate product categories
def generate_product_categories(num_categories):
    for _ in range(num_categories):
        name = fake.word().capitalize()
        
        parent_category_id = None if random.choice([True, False]) else fake.uuid4()  # Randomly assign a parent category

        cursor.execute(
            sql.SQL("INSERT INTO ProductCategories (name,parent_category_id) VALUES (%s,%s)"),
            (name,parent_category_id)
        )

# Generate data using the configuration from environment variables
generate_users(NUM_USERS)
generate_products(NUM_PRODUCTS)
generate_orders(NUM_ORDERS)
generate_order_details(NUM_ORDER_DETAILS)
generate_product_categories(NUM_CATEGORIES)

# Commit changes and close the connection
conn.commit()
cursor.close()
conn.close()
