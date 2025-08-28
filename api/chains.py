import json
from os import getenv

from db import connection
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableBranch, RunnablePassthrough
from langchain_ollama.chat_models import ChatOllama
from sqlalchemy import text
from templates import response_template, sql_template

load_dotenv()

db_uri = "postgresql+psycopg2://llm:0000123450000@postgres:5432/ponyfin"

db = SQLDatabase.from_uri(
    db_uri,
    view_support=True,
    include_tables=["budgets", "categories", "expenses", "incomes"],
)

loged_sql = ""


def make_response(user_id, question):
    response = run_full_chain(user_id, question)

    with connection.cursor() as cur:
        cur.execute(
            "INSERT INTO execution_log (user_id, question, generated_sql, response) VALUES (%s, %s, %s, %s)",
            (
                user_id,
                question,
                loged_sql,
                response["answer"],
            ),
        )
        connection.commit()

    return response


def get_schema(_):
    schema = db.get_table_info()
    return schema


llm = ChatOllama(
    model=getenv("MODEL_NAME"),
    stream=False,
    base_url="http://ollama:11434",
    temperature=0,
)


def run_with_user_id(user_id: int, sql_query: str):
    global loged_sql
    loged_sql = sql_query
    engine = db._engine
    with engine.begin() as conn:
        conn.execute(
            text("SET LOCAL app.current_user_id = :user_id"), {"user_id": user_id}
        )
        result = conn.execute(text(sql_query))
        if result.returns_rows:
            return result.fetchall()
        return None


def run_full_chain(user_id, question):
    prompt = ChatPromptTemplate.from_template(sql_template)

    sql_chain = (
        RunnablePassthrough.assign(schema=get_schema)
        | prompt
        | llm
        | StrOutputParser()
        | (lambda s: json.loads(s))
    )

    prompt_response = ChatPromptTemplate.from_template(response_template)

    branch = RunnableBranch(
        (
            lambda vars: vars["query"]["sql"] is True,
            RunnablePassthrough.assign(
                schema=get_schema,
                response=lambda vars: run_with_user_id(
                    user_id, vars["query"]["response"]
                ),
            )
            | prompt_response
            | llm
            | StrOutputParser(),
        ),
        (
            RunnablePassthrough.assign(
                schema=get_schema, response=lambda vars: vars["query"]["response"]
            )
            | prompt_response
            | llm
            | StrOutputParser()
        ),
    )

    full_chain = RunnablePassthrough.assign(query=sql_chain) | branch

    return {
        "answer": full_chain.invoke({"question": question}),
    }
