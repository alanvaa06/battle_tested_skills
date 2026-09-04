import sqlalchemy

from demo.core.base import Repo


class PgRepo(Repo):
    def get(self, key: str) -> str:
        return str(sqlalchemy.__version__) + key
