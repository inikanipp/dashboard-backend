from importlib.resources import contents
import io
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
import polars as pl

from config.database import get_db

# Import semua repository
from repository.repository_city import RepositoryCity
from repository.repository_method import RepositoryMethod
from repository.repository_product import RepositoryProduct
from repository.repository_retailer import RepositoryRetailer
from repository.repository_transaction import RepositoryTransaction
from service.service_cleaning import ServiceTransaction
from service.service_polars import ServicePolars

router = APIRouter()

@router.post("/upload-transaction")
async def upload_transaction_excel(
    file: UploadFile = File(...), 
    filtered: Optional[str] = Form(None), # Tangkap parameter filter
    product: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    method: Optional[str] = Form(None),
    uploaded_by: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    service_polars_tool: ServicePolars = Depends(ServicePolars)
):
    repo_city = RepositoryCity(db)
    repo_method = RepositoryMethod(db)
    repo_product = RepositoryProduct(db)
    repo_retailer = RepositoryRetailer(db)
    repo_transaction = RepositoryTransaction(db)

    service = ServiceTransaction(
        repo_city=repo_city,
        repo_method=repo_method,
        repo_product=repo_product,
        repo_retailer=repo_retailer,
        repo_transaction=repo_transaction,
        service_polars=service_polars_tool
    )

    # Kirim parameter filter ke service
    result = await service.process_excel_users(
        file=file,
        filtered=filtered,
        product=product,
        state=state,
        city=city,
        method=method
    )
    
    # Amankan return jika result berupa dictionary atau list
    saved_count = result.get("total", 0) if isinstance(result, dict) else len(result)
    return {"status": "success", "saved": saved_count}


@router.post("/preview")
async def preview_adidas_excel(
    file: UploadFile = File(...), 
    db: AsyncSession = Depends(get_db),
    service_polars_tool: ServicePolars = Depends(ServicePolars)
):
    try:
        if not file.filename.endswith((".xlsx", ".xls")):
            raise HTTPException(400, "File harus berupa Excel (.xlsx atau .xls)")

        contents = await file.read()
        df = pl.read_excel(io.BytesIO(contents))

        repo_city = RepositoryCity(db)
        try:
            list_city = await repo_city.get_list_city()
        except Exception:
            list_city = [] 

        # Proses cleaning data keseluruhan
        cleaned_df = service_polars_tool.execute_all(
            dataframe=df,
            list_normalize=list_city,
            department='Retailer'
        )

        if "Invoice Date" in cleaned_df.columns:
            cleaned_df = cleaned_df.with_columns(
                pl.col("Invoice Date").dt.to_string("%Y-%m-%d")
            )

        unique_products = cleaned_df["Product"].drop_nulls().unique().to_list() if "Product" in cleaned_df.columns else []
        unique_states = cleaned_df["State"].drop_nulls().unique().to_list() if "State" in cleaned_df.columns else []
        unique_cities = cleaned_df["City"].drop_nulls().unique().to_list() if "City" in cleaned_df.columns else []
        unique_methods = cleaned_df["Sales Method"].drop_nulls().unique().to_list() if "Sales Method" in cleaned_df.columns else []

        unique_products.sort()
        unique_states.sort()
        unique_cities.sort()
        unique_methods.sort()

        preview_data = cleaned_df.head(20).to_dicts()

        total_rows = len(cleaned_df)
        valid_rows = len(cleaned_df.filter(pl.col("Total Sales") > 0))
        invalid_rows = total_rows - valid_rows

        return {
            "status": "success",
            "preview": preview_data,
            "total_rows": total_rows,
            "valid_rows": valid_rows,
            "invalid_rows": invalid_rows,
            "columns": cleaned_df.columns,
            "filter_options": {
                "products": unique_products,
                "states": unique_states,
                "cities": unique_cities,
                "methods": unique_methods
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saat memproses file: {str(e)}")


@router.get("/test")
async def test_endpoint():
    """Test endpoint"""
    return {"status": "ok", "message": "API is running"}