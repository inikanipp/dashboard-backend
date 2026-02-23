from pydantic import BaseModel
from datetime import date

class RawSalesInput(BaseModel):
    Retailer: str = "Ramayana" # Default jika tidak ada di gambar
    Region: str
    State: str
    City: str
    Product_Raw: str  # Contoh: "Men's Street Footwear"
    Price_per_Unit: float
    Operating_Margin: float
    Sales_Method: str
    Transaction_Date: date # Kita butuh ini untuk ekstraksi Month, DayofWeek, Week


# class MinimalPredictionInput(BaseModel):
#     Retailer: str
#     City: str
#     Product_Raw: str
#     Operating_Margin: float
#     Sales_Method: str


class MinimalPredictionInput(BaseModel):
    Retailer: str
    City: str
    Product_Raw: str
    New_Operating_Margin: float  # Margin custom yang ingin diuji
    Sales_Method: str