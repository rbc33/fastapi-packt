import sqlite3
from typing import Any
from contextlib import contextmanager

from app.api.schemas.shipment import ShipmentCreate, ShipmentUpdate, ShipmentStatus


class Database:
    
    def connect_to_db(self):
        self.conn = sqlite3.connect("sqlite.db", check_same_thread=False)
        self.cur = self.conn.cursor()


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
        # # result = cursor.fetchall()
        # # result = cursor.fetchmany(2)
        # result = cursor.fetchone()

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

    # def __enter__(self):
    #     # print("Entering the context manager")
    #     self.connect_to_db()
    #     self.create_table()
    #     return self

    # def __exit__(self, *arg):
    #     # print("Exiting the context manager")
    #     self.close()


@contextmanager
def managed_db():
    db = Database()
    db.connect_to_db()
    db.create_table()
    yield db
    db.close()

with managed_db() as db:
    print(db.get(1))
    print(db.get_last())
    print(db.create(ShipmentCreate(content="laptop", weight=20.0)))
    print(db.get_last())
    print(db.update(1, ShipmentUpdate(status=ShipmentStatus.in_transit)))
    print(db.get(1))
    print(db.get(1))
