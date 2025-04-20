import requests as r
from dotenv import load_dotenv
import os


class Covid_Etl:
    load_dotenv()
    def __init__(self):
        self.covid_apininja_pop_endpoint = 'https://api.api-ninjas.com/v1/population'
        self.all_countries_name_endpoint = 'https://restcountries.com/v3.1/all'
        self.regions_endpoint = 'https://covid-api.com/api/regions' # This is the endpoint to fetch the regions (the countries in the world) and and the ISOs 
        self.province_endpoint = 'https://covid-api.com/api/provinces'
        self.country_details = self.fetch_country_details() # This fetches all the countries with their names and additional details. 
        self.regions = self.get_regions()

    def extract_covid_data(self):
        pass

    def transform_covid_data(self):
        pass

    
    def get_population(self, iso: str) -> int:
        """
        Fetches the population of a given country based on the ISO code using the World Bank API
        
        Args:
            iso: this is the ISO3 code for the country
            
        Returns:
            An integer of the population figure
        """
        endpoint = f'https://api.worldbank.org/v2/country/{iso}/indicator/SP.POP.TOTL'
        parameters = {
            'date': 2020,
            'format': 'json'
        }

        try:
            response = r.get(url=endpoint, params=parameters)
            data = response.json()
            return data[1][0]['value']
        except TypeError:
            return None
        except IndexError:
            return None
    
    def enter_parameters(self, country_identifier: str):
        """
        Fetches the details of a country including its population. 
        
        Args:
            country_identifier: this is the name or iso of the desired country e.g China or CHN
        
        Returns:
            a json object containing the information.
        """
        endpoint = self.covid_apininja_pop_endpoint
        API_KEY =  os.getenv('API_KEY')
        PARAMETERS = {
            'X-Api-Key': API_KEY,
            'country': country_identifier
        }
        response = r.get(endpoint, PARAMETERS)
        data = response.json()
        return data

    def get_population_retry(self, country_name: str):
        """
        Fetches the population of a desired country when the original function fails
        
        Args:
            country_name: This is the name of the country e.g Nigeria.
        
        Returns:
            Integer of the population
        """
        endpoint = f'https://d6wn6bmjj722w.population.io/1.0/population/2020/{country_name}'
        response = r.get(endpoint)
        data = response.json()
        total_population = sum(data[i]['total'] for i in range(len(data)))
        return total_population
        
    def get_country_population(self, **kwargs):
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
            data = self.enter_parameters(country_identifier=country)
            try:
                print(country)
                population = data['historical_population'][3]['population'] # This gets the population of the requested country
                # p.pprint(data['historical_population'][3]['year']) 
            except TypeError:
                try:
                    data = self.enter_parameters(country_identifier=iso)
                    population = data['historical_population'][3]['population'] # This gets the population of the requested country
                except TypeError:
                    try:
                        population = self.get_population_retry(country_name=official_name)
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
    
    def _crosscheck_country(self, **country_details):
        """
        Fetches country name after cross checking the detailsusing either country or ISO code: 

        Args:
        all_countries: a json object containing all the required names of all the countries in the world. 
        country: country name (e.g., 'China')
        iso: ISO code (e.g., 'CHN')

        Returns: 
        tuple of the correct country name and ISO
        """
        country = country_details.get('country')
        iso = country_details.get('iso')
        all_countries = country_details.get('all_countries')

        country_name = [([all_countries[correct_country]['name']['common'], all_countries[correct_country]['name']['official']], all_countries[correct_country]['cca3']) for correct_country in range(len(all_countries)) if all_countries[correct_country]['cca3'] in iso]
        if not country_name:
            country_name = [([all_countries[correct_country]['name']['common'], all_countries[correct_country]['name']['official']], all_countries[correct_country]['cca3']) for correct_country in range(len(all_countries)) if country in all_countries[correct_country]['name']['common']]
        return country_name
    
    def get_regions(self):
        """
        Fetch all the regions from the HSBU database via API

        Returns:
            A json object containing the ISO3 code and names of the regions documented in the database e.g. ({'iso': 'CHN', 'name': 'China'})
        """
        response = r.get(f'{self.regions_endpoint}')
        r_data = response.json()

        return r_data['data']
    
    def get_provinces(self, iso: str):
        """
        Fetch all the regions from the HSBU database via API

        Args:
            Takes the iso of the country e.g. for Nigeria, 'NGA'

        Returns:
            a json object containing the ISO3 of the country the province belongs to, longitude and latitude of the province and name of the province
        """
        p_response = r.get(url=self.province_endpoint, params={'iso': iso})
        p_data = p_response.json()
        return p_data['data']
    
f = Covid_Etl()
print(f.get_provinces('CHN'))