from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from models.model_transaction import City, Product, State, Transaction
# from models import User

class RepositoryTransaction :
    def __init__(self, db : AsyncSession) :
        self.db = db

    async def insert_transactions(self, transactions_data: list[dict]):

        try:
            new_entries = [Transaction(**data) for data in transactions_data]
            
            self.db.add_all(new_entries)
            await self.db.commit()
            return {"status": "success", "total": len(new_entries)}
        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_state_from_city(self, city_name: str):
        """Mencari Nama State (Provinsi) dari Nama Kota melalui ID."""
        # Jika error 'attribute nama', ganti .name menjadi .nama
        query = (
            select(State.state.label("state_name")) 
            .join(City, City.id_state == State.id_state)
            .where(City.city == city_name)
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.fetchone()

    async def get_latest_history(self, product_raw_name: str, city_name: str):
        """
        Mengambil Harga Unit & Operating Margin terakhir dari database.
        Melakukan JOIN karena Transaction hanya berisi ID.
        """
        query = (
            select(
                Transaction.price_per_unit,
                Transaction.operating_margin
            )
            .join(Product, Transaction.id_product == Product.id_product)
            .join(City, Transaction.id_city == City.id_city)
            .where(Product.product == product_raw_name)
            .where(City.city == city_name)
            .order_by(desc(Transaction.invoice_date))
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.fetchone()