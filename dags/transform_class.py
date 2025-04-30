import pandas as pd
import numpy as np
import logging
from datetime import datetime

class CovidTransformer:
    def __init__(self):
        self.country_map = {}


    def _country_dim(self, raw_data: dict) -> pd.DataFrame:
        """
        This creates the DIM_COUNRTY with SCD Type 2 support

        :params:   
            raw_data: this is a dictionary containing the values for the counntry details from the COVID extractor class

        :returns:
            a Pandas dataframe that contains the country dim
                DIM_COUNTRY {
                    country_id INT PK
                    iso_code VARCHAR UNIQUE
                    country_name VARCHAR
                    population INT
                }
        """
        countries = raw_data['daily_reports'][['iso', 'country']].drop_duplicates()  # Fetching the iso_code and country_name
        country_data = pd.merge(
            countries,
            raw_data['population'],
            on='iso',
            how='left'
        )  # inner join with the population data to fetch the population. 

        # Fetching the country_id
        country_id = lambda df: df['iso'].apply(
            lambda x: self.country_map.setdefault(x, len(self.country_map) + 1)
        )

        # Adding additional colums to promote SCD Type 2
        dim_country = country_data.assign(
            country_id=country_id,
            valid_from=datetime(2020, 1, 1),
            valid_to=datetime(9999, 12, 31)
        ).rename(
            columns={
                'country': 'country_name',
                'iso': 'iso_name'
            }
            )[['country_id', 'iso_code', 'country_name', 'population', 'valid_from', 'valid_to']]
        
        return dim_country