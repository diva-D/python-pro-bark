from select import select
import sqlite3
from sqlite3 import Cursor
from typing import Any


class DatabaseManager:
    def __init__(self, database_path: str) -> None:
        self.connection = sqlite3.connect(database_path)

    def __del__(self):
        self.connection.close()

    def _execute(self, statement: str, parameters: list[Any] = None) -> Cursor:
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(statement, parameters or [])
            return cursor

    def create_table(self, table_name: str, columns: dict[str, str]) -> None:
        column_strs = [
            f"{column_name} {column_values}"
            for column_name, column_values in columns.items()
        ]
        statement = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {(', ').join(column_strs)}
        )
        """
        self._execute(statement)

    def add(self, table: str, data: dict[str, Any]) -> None:
        placeholders = ", ".join("?" * len(data))
        column_names = (", ").join(data.keys())
        column_values = tuple(data.values())
        self._execute(
            f"""
            INSERT INTO {table}
            ({column_names})
            VALUES ({placeholders})
            """,
            column_values,
        )

    def delete(self, table: str, criteria: dict[str, Any]) -> None:
        placeholders = [f"{column} = ?" for column in criteria.keys()]
        delete_criteria = " AND ".join(placeholders)
        self._execute(
            f"""
            DELETE FROM {table}
            WHERE {delete_criteria}
            """,
            tuple(criteria.values()),
        )

    def select(
        self,
        table: str,
        columns: list = None,
        criteria: dict[str, Any] = None,
        order_by: str = None,
    ) -> None:
        select_columns = ", ".join(columns or ["*"])
        placeholders = [f"{column} = ?" for column in criteria]
        delete_criteria = " AND ".join(placeholders)
        self._execute(
            f"""
            SELECT {select_columns} FROM {table}
            WHERE {delete_criteria}
            {f"ORDER BY {order_by}" if order_by else ""}
            """,
            tuple(criteria.values()),
        )
