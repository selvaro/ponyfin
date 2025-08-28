from os import getenv

import psycopg2
from dotenv import load_dotenv

load_dotenv()

connection = psycopg2.connect(
    host="postgres",
    database=getenv("DB_NAME"),
    user=getenv("DB_USER"),
    password=getenv("DB_USER_PASSWORD"),
    port="5432",
)

cursor = connection.cursor()


def get_user_registered(user_id):
    sql_string = "SELECT id FROM users WHERE telegram_id = %s"

    cursor.execute(sql_string, (user_id,))

    try:
        id = cursor.fetchone()
    except psycopg2.Error:
        return False

    return id[0]


def insert_user(payload):
    sql_string = "INSERT INTO users (telegram_id, name) VALUES (%s, %s) RETURNING id, registration_date"

    cursor.execute(sql_string, (payload["telegram_id"], payload["name"]))
    row = cursor.fetchone()
    connection.commit()

    return [row[0], row[1]]
