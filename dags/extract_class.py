import requests as r
from dotenv import load_dotenv
import os
import pandas as pd
# rom typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging


class CovidAPIClient:
    """
    This is the contains the base URL of the COVID endpoint and ensures sessions for calling the API is maintained
    """
    COVID_ENDPOINT = 'https://covid-api.com/api'

    def __init__(self):
        self.session = r.Session()
        self.session.headers.update({'Accept': 'application/json'})
        self.logger = logging.getLogger(__name__)

    def _get_endpoint(self, endpoint: str, params: dict | None = None) -> dict:
        try:
            response = self.session.get(f'{self.COVID_ENDPOINT}/{endpoint}', params=params)
            response.raise_for_status()
            return response.json()
        except r.exceptions.RequestException as e:
            self.logger.error(f'API request has failed: {str(e)}')
            raise

class PopulationExtraction:
    """Handles retrieving population information from varying API endpoints"""
    def __init__(self):
        self.WB_ENDPOINT = 'https://api.worldbank.org/v2/country/{iso}/indicator/SP.POP.TOTL'
        self.enter_parameters_endpoint = 'https://api.api-ninjas.com/v1/population'
        self.get_population_retry_endpoint = 'https://d6wn6bmjj722w.population.io/1.0/population/2020/{country_name}'
        self.all_countries_name_endpoint = 'https://restcountries.com/v3.1/all'
        self.all_countries = self._fetch_country_details()
    def _get_population(self, iso: str) -> int:
        """
        Fetches the population of a given country based on the ISO code using the World Bank API
        
        Args:
            iso: this is the ISO3 code for the country
            
        Returns:
            An integer of the population figure
        """
        parameters = {
            'date': 2020,
            'format': 'json'
        }

        try:
            response = r.get(url=self.WB_ENDPOINT.format(iso=iso), params=parameters)
            data = response.json()
            return data[1][0]['value']
        except (TypeError, IndexError):
            return None
    def _enter_parameters(self, country_identifier: str):
        """
        Fetches the details of a country including its population. 
        
        Args:
            country_identifier: this is the name or iso of the desired country e.g China or CHN
        
        Returns:
            a json object containing the information.
        """
        
        API_KEY =  os.getenv('API_KEY')
        PARAMETERS = {
            'X-Api-Key': API_KEY,
            'country': country_identifier
        }
        response = r.get(self.enter_parameters_endpoint, PARAMETERS)
        data = response.json()
        return data
    def _get_population_retry(self, country_name: str) -> int:
        """
        Fetches the population of a desired country when the original function fails
        
        Args:
            country_name: This is the name of the country e.g Nigeria.
        
        Returns:
            Integer of the population
        """
        response = r.get(self.get_population_retry_endpoint.format(country_name=country_name))
        data = response.json()
        total_population = sum(data[i]['total'] for i in range(len(data)))
        return total_population

    def _get_country_population(self, **kwargs) -> int:
        """
        Fetches population data using either country or ISO code: 

        Args:
            country: country name (e.g., 'China')
            iso: ISO code (e.g., 'CHN')
            official_name: the official--formal--name of the country.

        Returns: 
            Integer of the population
        
        """
        country = kwargs.get('country')
        iso = kwargs.get('iso')
        official_name = kwargs.get('official_name')
        population = None
        
        if country:
            data = self._enter_parameters(country_identifier=country)
            try:
                print(country)
                population = data['historical_population'][3]['population'] # This gets the population of the requested country
                # p.pprint(data['historical_population'][3]['year']) 
            except TypeError:
                try:
                    data = self._enter_parameters(country_identifier=iso)
                    population = data['historical_population'][3]['population'] # This gets the population of the requested country
                except TypeError:
                    try:
                        population = self._get_population_retry(country_name=official_name)
                    except KeyError:
                        pass
        return population  


    def _fetch_country_details(self):
        """
        Fetches all the names and additional details of every country in the world:
        
        Returns: 
        A json object containing all the countries in the world. 
        
        TIP: access this function from a variable to avoid timeouts. 
        
        This function is used in tandem with the function `crosscheck_country`. It is the argument `all_countries`.

        """
        endpoint = self.all_countries_name_endpoint
        response = r.get(endpoint)
        data = response.json()
        return data
    
    def _crosscheck_country(self, **country_details) -> list[tuple]:
        """
        Fetches country name after cross checking the details using either country or ISO code: 

        Args: 
        country: country name (e.g., 'China')
        iso: ISO code (e.g., 'CHN')

        Returns: 
        tuple of the correct country name, official country name and ISO
        """
        country = country_details.get('country')
        iso = country_details.get('iso')
        all_countries = self.all_countries

        country_names = [([all_countries[correct_country]['name']['common'], all_countries[correct_country]['name']['official']], all_countries[correct_country]['cca3']) for correct_country in range(len(all_countries)) if all_countries[correct_country]['cca3'] in iso]
        if not country_names:
            country_names = [([all_countries[correct_country]['name']['common'], all_countries[correct_country]['name']['official']], all_countries[correct_country]['cca3']) for correct_country in range(len(all_countries)) if country in all_countries[correct_country]['name']['common']]
        return country_names

    def return_population(self, **kwargs) -> int:
        """
        This takes all the methods in the PopulationExtract class and computes the population for a country. 
        This is the method to call as all other methods are modularised to serve varying purposes. 

        Args:
            country: country name (e.g., 'China')
            iso: ISO code (e.g., 'CHN')

        Returns:
            An integer of the desired country
        """
        iso = kwargs.get('iso')
        country = kwargs.get('country')
        all_countries = self.all_countries

        population = self._get_population(iso)
        if not population:
            country_details = self._crosscheck_country(country=country, iso=iso, all_countries=all_countries)
            try:
                population = self._get_country_population(country=country_details[0][0][0], iso=country_details[0][1], official_name=country_details[0][0][1])
            except IndexError:
                pass
        return population

class CountryExtraction(CovidAPIClient):
    """
    Handles the extraction of the country's details
    """
    def __init__(self):
        super().__init__()
        self.EARLIEST_COVID_DATE = datetime(2019, 12, 1)
        self.LATEST_COVID_DATE = datetime(2023, 3, 9)
    def get_regions(self) -> pd.DataFrame:
        """
        Fetch all the regions from the John Hopkins Witing School of Engineering database via API

        Returns:
            A pandas Dataframe containing the ISO3 code and names of the regions documented in the database
        """
        data = self._get_endpoint(endpoint='regions')

        return pd.DataFrame(data['data'])[['iso', 'name']]

    def get_covid_details(self, iso: str, date_string: str) -> pd.DataFrame:
        """
        Fetches the COVID data for a specific date and country using the ISO code

        Args:
            iso: the ISO3 code for the country
            date: the specific date within the COVID timeframe. The format is DD-MM-YYYY
        """
        # Check for edge case: the earliest date of the COVID-data
        
        

        date_string = datetime.strptime(date_string, "%d-%m-%Y")

        if date_string < self.EARLIEST_COVID_DATE:
            raise ValueError(f'The date {date_string} is earlier than the earliest recorded COVID case')
        
        if date_string > self.LATEST_COVID_DATE:
            raise ValueError(f'The date is ahead of the latest recorded COVID date in the database')
        
        parameters = {
            'iso': iso,
            'date': date_string.strftime('%Y-%m-%d')
        }

        try:
            data = self._get_endpoint('reports', parameters)
            if not data['data']:
                self.logger.warning(f'No data found for {iso} on {date_string}')
                return pd.DataFrame()
            return pd.DataFrame(data['data'])
        except (ValueError, KeyError) as e:
            self.logger.error(f'Failed to find any information: {str(e)}')
            raise
    
class ProvinceExtraction(CovidAPIClient):
    """
    Handles the data extraction on the provincial level
    """
    def get_provinces(self, iso: str) -> pd.DataFrame:
        """
        Fetch all the regions from the John Hopkins Witing School of Engineering database via API

        Args:
            Takes the iso of the country e.g. for Nigeria, 'NGA'

        Returns:
            a json object containing the ISO3 of the country the province belongs to, longitude and latitude of the province and name of the province
        """
        data = self._get_endpoint(endpoint='provinces', params={'iso': iso})
        return pd.DataFrame(data['data'])
    

class CovidExtractor:
    """
    This ochestrates all extraction processes.
    """
    def __init__(self):
        self.country_handling = CountryExtraction()
        self.population = PopulationExtraction()
        self.province_handling = ProvinceExtraction()

        countries = self.country_handling.get_regions()

    
