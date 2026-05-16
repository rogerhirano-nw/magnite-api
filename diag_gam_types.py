"""Diagnostic: print line_item_type distribution and order name samples."""
import os, sqlalchemy, pandas as pd

engine = sqlalchemy.create_engine(os.environ["DATABASE_URL"])

with engine.connect() as conn:
    df_types = pd.read_sql(
        sqlalchemy.text("""
            SELECT line_item_type, COUNT(*) as n
            FROM gam_campaigns
            GROUP BY line_item_type
            ORDER BY n DESC
        """), conn)
    print("=== line_item_type breakdown ===")
    print(df_types.to_string(index=False))

    df_orders = pd.read_sql(
        sqlalchemy.text("""
            SELECT DISTINCT line_item_type, order_name
            FROM gam_campaigns
            WHERE order_name NOT LIKE 'Newsweek_Direct%%'
              AND order_name NOT LIKE 'Newsweek_Test%%'
            ORDER BY line_item_type, order_name
            LIMIT 80
        """), conn)
    print("\n=== Non-Direct order names by line_item_type ===")
    print(df_orders.to_string(index=False))
