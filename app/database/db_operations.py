# coding: utf8
from pathlib import Path
from dataclasses import dataclass
from app.database.Sqlite3Helper import (
    Sqlite3Worker, Column, DataType,
    Operand, Table,
)

from app.chromy import get_browser_exec_path, get_browser_data_path
from app.common.utils import SUPPORTED_BROWSERS


@dataclass
class UserDataTable(Table):
    table: str = "userdata"

    id = Column("id", DataType.INTEGER, primary_key=True)
    name = Column("name", DataType.TEXT, unique=True)
    type = Column("type", DataType.TEXT)
    exec_path = Column("exec_path", DataType.TEXT)
    data_path = Column("data_path", DataType.TEXT)


U = UserDataTable()


class DBManger(object):

    def __init__(self):
        # self.app_dir = app_dir

        self.sqh = Sqlite3Worker(str(Path("./userdata.db")))
        self.sqh.create_table(U.table, U.all, if_not_exists=True)

        # 如果数据库为空，则可能是第一次打开，就创建默认的表
        _, results = self.sqh.select(U.table, U.all)
        if len(results) == 0:
            self.reset()

    def reset(self):
        self.sqh.delete_from(U.table)
        values = []
        for b in SUPPORTED_BROWSERS:
            dp = get_browser_data_path(b)
            if dp is None:
                continue

            ep = get_browser_exec_path(b)
            values.append([b.capitalize(), b, ep, dp])

        self.sqh.insert_into(U.table, [
            U.name, U.type, U.exec_path, U.data_path
        ], values)

    def select_all(self):
        _, results = self.sqh.select(U.table, [U.name, U.type, U.exec_path, U.data_path])
        return results

    def insert_one(self, name: str, type_: str, exec_path: str, data_path: str):
        self.sqh.insert_into(U.table, [
            U.name, U.type, U.exec_path, U.data_path
        ], [
            [name, type_, exec_path, data_path],
        ])

    def delete_one(self, name: str):
        self.sqh.delete_from(U.table, where=Operand(U.name).equal_to(name))
