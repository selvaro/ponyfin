from datetime import datetime, timedelta
from os import getenv

import psycopg2
from psycopg2.extras import RealDictCursor

TOOLS_JSON = """
[
    {
        "type": "function",
        "function": {
            "name": "list_categories",
            "description": "Retrieve all categories for the authenticated user.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_category",
            "description": "Add a new category for the authenticated user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string", "nullable": true}
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_category",
            "description": "Update an existing category for the authenticated user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "description": {"type": "string", "nullable": true}
                },
                "required": ["id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_category",
            "description": "Delete a category for the authenticated user (only if no linked expenses or budgets).",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"}
                },
                "required": ["id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_expense",
            "description": "Add a new expense for the authenticated user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "currency": {"type": "string"},
                    "date": {"type": "string", "format": "date-time"},
                    "category_id": {"type": "integer"},
                    "description": {"type": "string", "nullable": true}
                },
                "required": ["amount", "currency", "date", "category_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_expenses",
            "description": "Retrieve expenses for the authenticated user with optional filters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category_id": {"type": "integer", "nullable": true},
                    "currency": {"type": "string", "nullable": true},
                    "start_date": {"type": "string", "format": "date-time", "nullable": true},
                    "end_date": {"type": "string", "format": "date-time", "nullable": true},
                    "description": {"type": "string", "nullable": true},
                    "sort_by": {"type": "string", "enum": ["amount", "date"], "nullable": true},
                    "limit": {"type": "integer", "nullable": true}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_expense",
            "description": "Update an existing expense for the authenticated user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "amount": {"type": "number", "nullable": true},
                    "currency": {"type": "string", "nullable": true},
                    "date": {"type": "string", "format": "date-time", "nullable": true},
                    "category_id": {"type": "integer", "nullable": true},
                    "description": {"type": "string", "nullable": true}
                },
                "required": ["id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_expense",
            "description": "Delete an expense for the authenticated user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"}
                },
                "required": ["id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_expenses",
            "description": "Summarize expenses for the authenticated user with optional filters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category_id": {"type": "integer", "nullable": true},
                    "currency": {"type": "string", "nullable": true},
                    "start_date": {"type": "string", "format": "date-time", "nullable": true},
                    "end_date": {"type": "string", "format": "date-time", "nullable": true},
                    "group_by": {"type": "string", "enum": ["category", "date", "currency"], "nullable": true}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_income",
            "description": "Add a new income for the authenticated user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "currency": {"type": "string"},
                    "date": {"type": "string", "format": "date-time"},
                    "source": {"type": "string", "nullable": true}
                },
                "required": ["amount", "currency", "date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_incomes",
            "description": "Retrieve incomes for the authenticated user with optional filters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "currency": {"type": "string", "nullable": true},
                    "start_date": {"type": "string", "format": "date-time", "nullable": true},
                    "end_date": {"type": "string", "format": "date-time", "nullable": true},
                    "source": {"type": "string", "nullable": true},
                    "sort_by": {"type": "string", "enum": ["amount", "date"], "nullable": true},
                    "limit": {"type": "integer", "nullable": true}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_incomes",
            "description": "Summarize incomes for the authenticated user with optional filters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "currency": {"type": "string", "nullable": true},
                    "start_date": {"type": "string", "format": "date-time", "nullable": true},
                    "end_date": {"type": "string", "format": "date-time", "nullable": true},
                    "group_by": {"type": "string", "enum": ["source", "date", "currency"], "nullable": true}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_budget",
            "description": "Add a new budget for the authenticated user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "currency": {"type": "string"},
                    "month": {"type": "integer"},
                    "year": {"type": "integer"},
                    "category_id": {"type": "integer", "nullable": true}
                },
                "required": ["amount", "currency", "month", "year"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_budgets",
            "description": "Retrieve budgets for the authenticated user with optional filters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "currency": {"type": "string", "nullable": true},
                    "category_id": {"type": "integer", "nullable": true},
                    "month": {"type": "integer", "nullable": true},
                    "year": {"type": "integer", "nullable": true}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_budget",
            "description": "Check spending against budget for the authenticated user with optional filters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category_id": {"type": "integer", "nullable": true},
                    "currency": {"type": "string", "nullable": true},
                    "month": {"type": "integer", "nullable": true},
                    "year": {"type": "integer", "nullable": true}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_financial_advice",
            "description": "Provide financial advice for the authenticated user based on optional context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "context": {"type": "string", "nullable": true}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_data",
            "description": "Query any table for the authenticated user with custom filters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table": {"type": "string", "enum": ["expenses", "incomes", "budgets", "categories"]},
                    "filters": {
                        "type": "object",
                        "additionalProperties": true,
                        "nullable": true
                    },
                    "sort_by": {"type": "string", "nullable": true},
                    "limit": {"type": "integer", "nullable": true}
                },
                "required": ["table"]
            }
        }
    }
]
"""


def get_db_connection():
    return psycopg2.connect(
        dbname=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_USER_PASSWORD"),
        host="postgres",
        port="5432",
    )


def list_categories(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    query = """
        SELECT c.id, c.name, c.description, c.user_id
        FROM categories c
        WHERE c.user_id = %s
    """
    cursor.execute(query, (user_id,))
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    print(categories, flush=True)
    return categories


def add_category(user_id, name, description=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO categories (name, description, user_id)
        VALUES (%s, %s, %s)
        RETURNING id
    """
    cursor.execute(query, (name, description, user_id))
    new_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return new_id


def update_category(user_id, id, nhttps://github.com/selvaro/ponyfiname=None, description=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        UPDATE categories
        SET name = COALESCE(%s, name),
            description = COALESCE(%s, description)
        WHERE id = %s AND user_id = %s
        RETURNING id
    """
    cursor.execute(query, (name, description, id, user_id))
    updated = cursor.rowcount > 0
    conn.commit()
    cursor.close()
    conn.close()
    return updated


def delete_category(user_id, id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        DELETE FROM categories
        WHERE id = %s AND user_id = %s
        AND NOT EXISTS (
            SELECT 1 FROM expenses WHERE category_id = categories.id
            UNION
            SELECT 1 FROM budgets WHERE category_id = categories.id
        )
        RETURNING id
    """
    cursor.execute(query, (id, user_id))
    deleted = cursor.rowcount > 0
    conn.commit()
    cursor.close()
    conn.close()
    return deleted


def add_expense(user_id, amount, currency, date, category_id, description=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO expenses (amount, currency, date, description, user_id, category_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """
    cursor.execute(query, (amount, currency, date, description, user_id, category_id))
    new_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return new_id


def get_expenses(
    user_id,
    category_id=None,
    currency=None,
    start_date=None,
    end_date=None,
    description=None,
    sort_by=None,
    limit=None,
):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    query = """
        SELECT e.id, e.amount, e.currency, e.date, e.description, e.category_id, e.user_id
        FROM expenses e
        WHERE e.user_id = %s
    """
    params = [user_id]
    if category_id is not None:
        query += " AND e.category_id = %s"
        params.append(category_id)
    if currency is not None:
        query += " AND e.currency = %s"
        params.append(currency)
    if start_date is not None:
        query += " AND e.date >= %s"
        params.append(start_date)
    if end_date is not None:
        query += " AND e.date <= %s"
        params.append(end_date)
    if description is not None:
        query += " AND e.description ILIKE %s"
        params.append(f"%{description}%")
    if sort_by in ["amount", "date"]:
        query += f" ORDER BY e.{sort_by}"
    if limit is not None:
        query += " LIMIT %s"
        params.append(limit)
    cursor.execute(query, params)
    expenses = cursor.fetchall()
    cursor.close()
    conn.close()
    return expenses


def update_expense(
    user_id,
    id,
    amount=None,
    currency=None,
    date=None,
    category_id=None,
    description=None,
):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        UPDATE expenses
        SET amount = COALESCE(%s, amount),
            currency = COALESCE(%s, currency),
            date = COALESCE(%s, date),
            category_id = COALESCE(%s, category_id),
            description = COALESCE(%s, description)
        WHERE id = %s AND user_id = %s
        RETURNING id
    """
    cursor.execute(
        query, (amount, currency, date, category_id, description, id, user_id)
    )
    updated = cursor.rowcount > 0
    conn.commit()
    cursor.close()
    conn.close()
    return updated


def delete_expense(user_id, id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        DELETE FROM expenses
        WHERE id = %s AND user_id = %s
        RETURNING id
    """
    cursor.execute(query, (id, user_id))
    deleted = cursor.rowcount > 0
    conn.commit()
    cursor.close()
    conn.close()
    return deleted


def summarize_expenses(
    user_id,
    category_id=None,
    currency=None,
    start_date=None,
    end_date=None,
    group_by=None,
):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    query = """
        SELECT 
    """
    if group_by in ["category", "date", "currency"]:
        query += f"e.{group_by}, "
    query += """
        SUM(e.amount) as total_amount, COUNT(e.id) as count
        FROM expenses e
        WHERE e.user_id = %s
    """
    params = [user_id]
    if category_id is not None:
        query += " AND e.category_id = %s"
        params.append(category_id)
    if currency is not None:
        query += " AND e.currency = %s"
        params.append(currency)
    if start_date is not None:
        query += " AND e.date >= %s"
        params.append(start_date)
    if end_date is not None:
        query += " AND e.date <= %s"
        params.append(end_date)
    if group_by in ["category", "date", "currency"]:
        query += f" GROUP BY e.{group_by}"
    cursor.execute(query, params)
    summary = cursor.fetchall()
    cursor.close()
    conn.close()
    return summary


def add_income(user_id, amount, currency, date, source=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO incomes (amount, currency, date, source, user_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """
    cursor.execute(query, (amount, currency, date, source, user_id))
    new_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return new_id


def get_incomes(
    user_id,
    currency=None,
    start_date=None,
    end_date=None,
    source=None,
    sort_by=None,
    limit=None,
):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    query = """
        SELECT i.id, i.amount, i.currency, i.date, i.source, i.user_id
        FROM incomes i
        WHERE i.user_id = %s
    """
    params = [user_id]
    if currency is not None:
        query += " AND i.currency = %s"
        params.append(currency)
    if start_date is not None:
        query += " AND i.date >= %s"
        params.append(start_date)
    if end_date is not None:
        query += " AND i.date <= %s"
        params.append(end_date)
    if source is not None:
        query += " AND i.source ILIKE %s"
        params.append(f"%{source}%")
    if sort_by in ["amount", "date"]:
        query += f" ORDER BY i.{sort_by}"
    if limit is not None:
        query += " LIMIT %s"
        params.append(limit)
    cursor.execute(query, params)
    incomes = cursor.fetchall()
    cursor.close()
    conn.close()
    return incomes


def summarize_incomes(
    user_id, currency=None, start_date=None, end_date=None, group_by=None
):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    query = """
        SELECT 
    """
    if group_by in ["source", "date", "currency"]:
        query += f"i.{group_by}, "
    query += """
        SUM(i.amount) as total_amount, COUNT(i.id) as count
        FROM incomes i
        WHERE i.user_id = %s
    """
    params = [user_id]
    if currency is not None:
        query += " AND i.currency = %s"
        params.append(currency)
    if start_date is not None:
        query += " AND i.date >= %s"
        params.append(start_date)
    if end_date is not None:
        query += " AND i.date <= %s"
        params.append(end_date)
    if group_by in ["source", "date", "currency"]:
        query += f" GROUP BY i.{group_by}"
    cursor.execute(query, params)
    summary = cursor.fetchall()
    cursor.close()
    conn.close()
    return summary


def add_budget(user_id, amount, currency, month, year, category_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO budgets (amount, currency, month, year, user_id, category_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """
    cursor.execute(query, (amount, currency, month, year, user_id, category_id))
    new_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return new_id


def get_budgets(user_id, currency=None, category_id=None, month=None, year=None):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    query = """
        SELECT b.id, b.amount, b.currency, b.month, b.year, b.user_id, b.category_id
        FROM budgets b
        WHERE b.user_id = %s
    """
    params = [user_id]
    if currency is not None:
        query += " AND b.currency = %s"
        params.append(currency)
    if category_id is not None:
        query += " AND b.category_id = %s"
        params.append(category_id)
    if month is not None:
        query += " AND b.month = %s"
        params.append(month)
    if year is not None:
        query += " AND b.year = %s"
        params.append(year)
    cursor.execute(query, params)
    budgets = cursor.fetchall()
    cursor.close()
    conn.close()
    return budgets


def check_budget(user_id, category_id=None, currency=None, month=None, year=None):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    query = """
        SELECT b.amount as budget_amount,
               COALESCE(SUM(e.amount), 0) as spent_amount
        FROM budgets b
        LEFT JOIN expenses e ON b.category_id = e.category_id
            AND e.date >= %s AND e.date < %s
            AND e.currency = b.currency
        WHERE b.user_id = %s
    """
    params = [
        f"{year}-{month}-01",
        f"{year}-{month + 1}-01" if month < 12 else f"{year + 1}-01-01",
        user_id,
    ]
    if category_id is not None:
        query += " AND b.category_id = %s"
        params.append(category_id)
    if currency is not None:
        query += " AND b.currency = %s"
        params.append(currency)
    if month is not None:
        query += " AND b.month = %s"
        params.append(month)
    if year is not None:
        query += " AND b.year = %s"
        params.append(year)
    query += " GROUP BY b.id, b.amount"
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def get_financial_advice(user_id, context=None):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    query = """
        SELECT SUM(e.amount) as total_expenses,
               SUM(i.amount) as total_income
        FROM expenses e
        FULL OUTER JOIN incomes i ON e.user_id = i.user_id
        WHERE e.user_id = %s OR i.user_id = %s
        AND e.date >= %s AND e.date <= %s
        AND i.date >= %s AND i.date <= %s
    """
    start_date = (datetime.now().replace(day=1) - timedelta(days=30)).isoformat()
    end_date = datetime.now().isoformat()
    cursor.execute(
        query, (user_id, user_id, start_date, end_date, start_date, end_date)
    )
    financials = cursor.fetchone()
    cursor.close()
    conn.close()
    advice = (
        "Consider reviewing your spending if expenses exceed income."
        if financials["total_expenses"] > financials["total_income"]
        else "Your finances seem balanced."
    )
    return {"advice": attributes, "context": context}


def query_data(user_id, table, filters=None, sort_by=None, limit=None):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    query = f"SELECT * FROM {table} WHERE user_id = %s"
    params = [user_id]
    if filters:
        for key, value in filters.items():
            query += f" AND {key} = %s"
            params.append(value)
    if sort_by:
        query += f" ORDER BY {sort_by}"
    if limit:
        query += " LIMIT %s"
        params.append(limit)
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


FUNCTIONS_DICT = {
    "list_categories": list_categories,
    "add_category": add_category,
    "update_category": update_category,
    "delete_category": delete_category,
    "add_expense": add_expense,
    "get_expenses": get_expenses,
    "update_expense": update_expense,
    "delete_expense": delete_expense,
    "summarize_expenses": summarize_expenses,
    "add_income": add_income,
    "get_incomes": get_incomes,
    "summarize_incomes": summarize_incomes,
    "add_budget": add_budget,
    "get_budgets": get_budgets,
    "check_budget": check_budget,
    "get_financial_advice": get_financial_advice,
    "query_data": query_data,
}


def run_tool(user_id, function_name, args):
    if function_name not in FUNCTIONS_DICT:
        raise ValueError(f"Function '{function_name}' not found in FUNCTIONS_DICT")

    func = FUNCTIONS_DICT[function_name]
    try:
        if user_id is None:
            raise ValueError("user_id is required in args")

        args_dict = args.copy()

        result = func(user_id, **args_dict)

        return result
    except TypeError as e:
        raise ValueError(f"Invalid arguments for function '{function_name}': {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error executing function '{function_name}': {str(e)}")
