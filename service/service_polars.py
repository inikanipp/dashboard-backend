import polars as pl
from rapidfuzz import process, fuzz
from fastapi import HTTPException, UploadFile
from polars import DataFrame


class ServicePolars :

    def execute_all(self, dataframe : pl.DataFrame, list_normalize : list, department : str) :
        self.dataframe = dataframe
        self.list_normalize = list_normalize
        self.department = department

        self._search_info_department()
        self._fix_columsn_name()
        self._retailer_name()
        self._change_data_type()
        self._fix_merged_cell()
        self._fill_missing_values()
        self._normalize_city()
        self._fill_product()

        return self.dataframe

    def _search_info_department(self):
        df = self.dataframe
        posisi_lengkap = (
            df.with_row_index("row_nr")
            .unpivot(index="row_nr") 
            .filter(pl.col("value") == self.department)
        )

        if posisi_lengkap.is_empty() :
            HTTPException(404, 'gada identitas departemen')

        all_columns = df.columns

        koordinat_angka = []

        for row, col_name in zip(posisi_lengkap["row_nr"], posisi_lengkap["variable"]):
            col_idx = all_columns.index(col_name)
            koordinat_angka = [row, col_idx]

        retailer = df[koordinat_angka[0], koordinat_angka[1]+1]

        self.department = retailer
    

    def _fix_columsn_name(self):
        df = self.dataframe
        top_col = list(df.row(7))
        bottom_col = tuple(df.row(8))

        top_col[2] = bottom_col[2]
        top_col[3] = bottom_col[3]
        top_col = tuple(top_col)

        df = df.rename({old: new for old, new in zip(df.columns, top_col)})
        df = df[9:]
        self.dataframe = pl.DataFrame(df)
    

    def _retailer_name(self):
        df = self.dataframe
        df = df.with_columns(
            Retailer = pl.lit(self.department)
        )
        self.dataframe = df
    
    def _change_data_type(self) :
        df = self.dataframe
        df = df.with_columns(
            pl.col('Price per Unit').cast(pl.Float64),
            pl.col('Units Sold').cast(pl.Int16),
            pl.col('Total Sales').cast(pl.Float64),
            pl.col('Operating Profit').cast(pl.Float64),
            pl.col('Operating Margin').cast(pl.Float32),
            pl.col("Invoice Date").str.to_datetime("%Y-%m-%d %H:%M:%S").cast(pl.Date)
        )

        self.dataframe = df

    def _fix_merged_cell(self) :
        df = self.dataframe
        df = df.with_columns(
            pl.col('State').forward_fill(),
            pl.col('City').forward_fill(),
            pl.col('Sales Method').forward_fill()
        )
        self.dataframe = df

    def _fill_missing_values(self) :
        df = self.dataframe
        for i in range (0,5):
            df = df.with_columns(
                pl.col('Price per Unit').fill_null(pl.col('Total Sales')/pl.col('Units Sold')),
                pl.col('Units Sold').fill_null(pl.col('Total Sales')/pl.col('Price per Unit')),
                pl.col('Total Sales').fill_null(pl.col('Units Sold')*pl.col('Price per Unit')),
                pl.col('Operating Profit').fill_null(pl.col('Total Sales')*pl.col('Operating Margin')),
                pl.col('Operating Margin').fill_null(pl.col('Operating Profit')/pl.col('Total Sales'))
            )
        
        self.dataframe = df

    def _normalize_city(self) :
        
        self.list_normalize = [item.lower() for item in self.list_normalize]
        df = self.dataframe

        def fix_typo(text):
            if text is None: return None
            
            text_lower = text.lower().strip()
            
            match, score, _ = process.extractOne(text_lower, self.list_normalize, scorer=fuzz.WRatio)
            print(f"Input: {text} -> Match: {match} (Score: {score})")

            if score > 45:
                return match.title()
            else:
                return text

        df = df.with_columns(
            City = pl.col("City").map_elements(fix_typo, return_dtype=pl.String)
        )

        self.dataframe = df


    def _fill_product(self) :
        df = self.dataframe

        df = df.with_columns(
            ((pl.int_range(0, pl.len()) % 6) + 1).alias("ulang_6")
        )

        buah_map = {
            1: "Men's Apparel",
            2: "Women's Apparel",
            3: "Men's Street Footwear",
            4: "Men's Athletic Footwear",
            5: "Women's Street Footwear",
            6: "Women's Athletic Footwear"
        }

        df = df.with_columns([
            pl.col("ulang_6").cast(pl.Int64),
            pl.col("Product").cast(pl.String)
        ])

        df = df.with_columns(
            pl.col("Product").fill_null(
                pl.col("ulang_6").replace(buah_map, default=None, return_dtype=pl.String)
            )
        )

        df = df.drop('ulang_6')
        self.dataframe = df


