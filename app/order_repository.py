# TechScale: Data access layer
# Owns the database connection pool and all SQL queries.
# The service layer and routes must not import sqlalchemy or pyodbc directly.
#
# Cloud database behaviour to account for when configuring the pool:
#   pool_size     — persistent connections kept open at all times
#   max_overflow  — extra connections allowed above pool_size during traffic spikes
#   pool_pre_ping — verifies a pooled connection is still alive before using it;
#                   silently replaces any that Azure closed during an idle period
#   pool_recycle  — retires a connection after N seconds to prevent Azure's
#                   idle timeout from closing it underneath the pool

import urllib
from sqlalchemy import create_engine, text
from database_config import get_odbc_connection_string


_connection_string = get_odbc_connection_string()
if _connection_string is None:
    DATABASE_URL = None
    engine = None
else:
    _params = urllib.parse.quote_plus(_connection_string)
    DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={_params}"


# TODO 1: Create the SQLAlchemy engine with a connection pool.
# Configure it to handle high-concurrency traffic and Azure's idle-connection timeout.
# Use the pool settings documented above. After creating the engine, verify connectivity.
if DATABASE_URL is not None:
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=1800,
    )


# TODO 2: Add a function that returns the top 5 orders by total payment value.
# Join ORDERS, CUSTOMERS, and ORDER_PAYMENTS.
# Return dicts with order_id, customer_name, and total_value rounded to 2 decimal places.
def get_top_orders():
    if engine is None:
        raise RuntimeError(
            "Database settings are missing; configure .env or environment variables"
        )

    query = text(
        """
        SELECT TOP 5
            o.order_id,
            c.customer_name,
            SUM(op.payment_value) AS total_value
        FROM ORDERS o
        JOIN CUSTOMERS c ON o.customer_id = c.customer_id
        JOIN ORDER_PAYMENTS op ON o.order_id = op.order_id
        GROUP BY o.order_id, c.customer_name
        ORDER BY total_value DESC
        """
    )
    with engine.connect() as connection:
        rows = connection.execute(query).mappings().all()

    return [
        {
            "order_id": row["order_id"],
            "customer_name": row["customer_name"],
            "total_value": round(float(row["total_value"]), 2),
        }
        for row in rows
    ]


# Entry point

if __name__ == "__main__":
    print("=== Connection pool test ===")
    if engine is None:
        raise RuntimeError(
            "Database settings are missing; configure .env or environment variables"
        )
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1")).fetchone()
    print(f"[DB] Connection pool ready: {result}")

    print("\n=== Top orders query ===")
    orders = get_top_orders()
    for o in orders:
        print(f"  {o['order_id']} | {o['customer_name']} | ${o['total_value']:.2f}")
