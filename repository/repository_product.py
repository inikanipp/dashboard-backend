from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.model_transaction import Product


class RepositoryProduct :
    def __init__(self, db : AsyncSession):
        self.db = db

    async def get_map_product(self) :
            query = select(Product.id_product, Product.product)
            result = await self.db.execute(query)

            rows = result.all()

            return {row.product: row.id_product for row in rows}