import io
import polars as pl
from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from models.model_transaction import City
from repository.repository_city import RepositoryCity
from repository.repository_method import RepositoryMethod
from repository.repository_product import RepositoryProduct
from repository.repository_retailer import RepositoryRetailer
from repository.repository_transaction import RepositoryTransaction
from service.service_polars import ServicePolars


class ServiceTransaction:
    def __init__(
        self, 
        repo_city : RepositoryCity, 
        repo_method : RepositoryMethod, 
        repo_product : RepositoryProduct, 
        repo_retailer : RepositoryRetailer, 
        repo_transaction : RepositoryTransaction,
        service_polars : ServicePolars
    ):
        self.repo_city = repo_city
        self.repo_method = repo_method
        self.repo_product = repo_product
        self.repo_retailer = repo_retailer
        self.repo_transaction = repo_transaction
        self.service_polars = service_polars

    
    async def process_excel_users(
        self, 
        file: UploadFile,
        filtered: str = None,
        product: str = None,
        state: str = None,
        city: str = None,
        method: str = None
    ):

        contents = await file.read()
        df = pl.read_excel(io.BytesIO(contents))

        list_city = await self.repo_city.get_list_city()

        # Cleaning data seperti biasa
        df = self.service_polars.execute_all(
                department='Retailer',
                dataframe=df,
                list_normalize=list_city,
            )

        if filtered == 'true':
            if product and product != 'all':
                df = df.filter(pl.col("Product") == product)
            if state and state != 'all':
                df = df.filter(pl.col("State") == state)
            if city and city != 'all':
                df = df.filter(pl.col("City") == city)
            if method and method != 'all':
                df = df.filter(pl.col("Sales Method") == method)

        city_map = await self.repo_city.get_map_city()
        method_map = await self.repo_method.get_map_method()
        product_map = await self.repo_product.get_map_product()
        retailer_map = await self.repo_retailer.get_map_retailer()

        transactions_to_insert = []

        for row in df.to_dicts():
            city_id = city_map.get(row["City"])
            product_id = product_map.get(row["Product"])
            retailer_id = retailer_map.get(row["Retailer"])
            method_id = method_map.get(row["Sales Method"])

            transaction_entry = {
                "id_city": city_id,
                "id_product": product_id,
                "id_retailer": retailer_id,
                "id_method": method_id,
                "invoice_date": row.get("Invoice Date"),
                "price_per_unit": row.get("Price per Unit"),
                "unit_sold": row.get("Units Sold"),
                "total_sales": row.get("Total Sales"),
                "operating_profit": row.get("Operating Profit"),
                "operating_margin": row.get("Operating Margin")
            }
            transactions_to_insert.append(transaction_entry)
        
        print(f"DEBUG: Data siap insert = {len(transactions_to_insert)} baris")

        # Cegah insert jika data kosong setelah di-filter
        if not transactions_to_insert:
            return []

        return await self.repo_transaction.insert_transactions(transactions_to_insert)