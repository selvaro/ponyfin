from os import getenv

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def log_tools(user_id, question, tools_called, response, tools_results):
    sql_string = "INSERT INTO execution_log (user_id, question, tools_called, ai_response, tools_results) VALUES (%s, %s, %s, %s, %s)"

    connection = psycopg2.connect(
        host="postgres",
        database=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_USER_PASSWORD"),
        port="5432",
    )

    with connection.cursor() as cur:
        cur.execute(
            sql_string, (user_id, question, tools_called, response, tools_results)
        )
        connection.commit()

    connection.close()
    cur.close()


def get_user_registered(user_id):
    sql_string = "SELECT id FROM users WHERE telegram_id = %s"

    connection = psycopg2.connect(
        host="postgres",
        database=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_USER_PASSWORD"),
        port="5432",
    )

    with connection.cursor() as cursor:
        cursor.execute(sql_string, (user_id,))

        try:
            id = cursor.fetchone()
        except psycopg2.Error:
            return False

    connection.close()
    cursor.close()

    return id


def insert_user(payload):
    sql_string = "INSERT INTO users (telegram_id, name) VALUES (%s, %s) RETURNING id, registration_date"

    connection = psycopg2.connect(
        host="postgres",
        database=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_USER_PASSWORD"),
        port="5432",
    )

    with connection.cursor() as cursor:
        cursor.execute(sql_string, (payload["telegram_id"], payload["name"]))
        row = cursor.fetchone()
        connection.commit()

    connection.close()
    cursor.close()

    return [row[0], row[1]]
