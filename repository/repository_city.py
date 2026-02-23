from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.model_transaction import City


class RepositoryCity :
    def __init__(self, db : AsyncSession):
        self.db = db

    async def get_map_city(self) :
        query = select(City.id_city, City.city)
        result = await self.db.execute(query)

        rows = result.all()

        return {row.city: row.id_city for row in rows}
    
    async def get_list_city(self) :
        query = select(City.city)
        result = await self.db.execute(query)

        rows = result.all()

        return [row[0] for row in rows]

