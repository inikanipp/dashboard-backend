from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.model_transaction import Method


class RepositoryMethod :
    def __init__(self, db : AsyncSession):
        self.db = db

    async def get_map_method(self) :
        query = select(Method.id_method, Method.method)
        result = await self.db.execute(query)

        rows = result.all()

        return {row.method: row.id_method for row in rows}