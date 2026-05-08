from abc import ABC
import asyncpg

class BaseRepository(ABC):

    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

