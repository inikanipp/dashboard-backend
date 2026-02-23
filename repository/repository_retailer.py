from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.model_transaction import Retailer


class RepositoryRetailer :
    def __init__(self, db : AsyncSession):
        self.db = db

    async def get_map_retailer(self) :
        query = select(Retailer.id_retailer, Retailer.retailer_name)
        result = await self.db.execute(query)

        rows = result.all()

        return {row.retailer_name : row.id_retailer for row in rows}