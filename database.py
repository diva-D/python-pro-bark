import sqlite3
from sqlite3 import Cursor
from typing import Any, Union


class DatabaseManager:
    def __init__(self, database_path: str) -> None:
        self.connection = sqlite3.connect(database_path)

    def __del__(self):
        self.connection.close()

    def _execute(self, statement: str, parameters: Union[None, tuple[Any]] = None) -> Cursor:
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

    def delete(self, table: str, criteria: dict[str, str]) -> None:
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
        columns: Union[None, list[str]] = None,
        criteria: Union[None, dict[str, str]] = None,
        order_by: Union[None, str] = None,
    ) -> Cursor:
        select_columns = ", ".join(columns or ["*"])
        query: str = f"SELECT {select_columns} FROM {table}"
        if columns is not None:
            placeholders: list[str] = [f"{column} = ?" for column in columns]
            select_criteria = " AND ".join(placeholders)
            query += f" WHERE {select_criteria}"
        if order_by is not None:
            query += f" ORDER BY {order_by}"
        return self._execute(
            query,
            tuple(criteria.values()) if criteria is not None else None,
        )
