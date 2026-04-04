import sqlite3
from typing import Any

import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.schemas import ShipmentCreate, ShipmentUpdate


class Database:
    def __init__(self):
        self.conn = sqlite3.connect("sqlite.db", check_same_thread=False)
        self.cur = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS shipments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT ,
                weight REAL ,
                status TEXT 
            )
        """
        )

    def create(self, shipment: ShipmentCreate) -> int:
        self.cur.execute(
            """
            INSERT INTO shipments (content, weight, status)
            VALUES (:content, :weight, :status)
        """,
            {
                **shipment.model_dump(),
                "status": "placed",
            },
        )
        self.conn.commit()
        return self.cur.lastrowid

    def get(self, id: int) -> dict[str, Any] | None:
        self.cur.execute(
            """
            SELECT * FROM shipments WHERE id = ?
        """,
            (id,),
        )
        row = self.cur.fetchone()

        return (
            {"id": row[0], "content": row[1], "weigth": row[2], "status": row[3]}
            if row
            else None
        )

    def get_last(self) -> dict[str, Any] | None:
        return self.get(self.cur.lastrowid)

    def update(self, id: int, shipment: ShipmentUpdate) -> dict[str, Any] | None:
        self.cur.execute(
            """
            UPDATE shipments SET status = :status WHERE id = :id
        """,
            {**shipment.model_dump(), "id": id},
        )
        return self.get(id)

    def delete(self, id: int):
        self.cur.execute(
            """
            DELETE FROM shipments WHERE id = ?
        """,
            (id,),
        )

    def drop_table(self):
        self.cur.execute(
            """
            DROP TABLE IF EXISTS shipments
        """
        )
    def close(self):
        self.conn.close()

# cursor.execute(
#     """
#     SELECT * FROM shipments
# """
# )
# # result = cursor.fetchall()
# # result = cursor.fetchmany(2)
# result = cursor.fetchone()
# print(result)

# connection.close()
# Database().drop_table()