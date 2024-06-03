from Devinci.config import debug
from Devinci.db.Entities import *
from Devinci.db.Management import Manager

from uuid import uuid4
import mysql.connector as mysql

class Service(ABC):
    @staticmethod
    def get_all() -> List[Entity]:
        pass

    @staticmethod
    def get(MAC:str, *args) -> List[Entity]:
        pass

    @staticmethod
    def add(PK:str, *args) -> None:
        pass

    @staticmethod
    def update(PK:str, *args) -> None:
        pass

    @staticmethod
    def delete(PK:str, *args) -> None:
        pass

    @staticmethod
    def exists(PK:str) -> bool:
        pass
    