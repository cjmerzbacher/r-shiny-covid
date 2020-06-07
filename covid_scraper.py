#Import required packages
import requests
import json
import codecs
from datetime import datetime
import time
import pandas as pd
from sys import argv

cases_url = "https://opendata.arcgis.com/datasets/a3a465675e824f4db499ce391f419f4e_0.geojson"
testing_url = "https://opendata.arcgis.com/datasets/ab7e55cbf46549aab626eab4bec4eba3_0.geojson"
hospital_url = "https://opendata.arcgis.com/datasets/7735f633986a4933ab1ff1294bb0e741_0.geojson"
deaths_url = "https://opendata.arcgis.com/datasets/b97ddd02a32847e3b54ddc79fb843837_0.geojson"
time_url = "https://opendata.arcgis.com/datasets/9f22d31b07014e02a5039f8baabf2322_0.geojson"

cases_response = requests.get(cases_url, timeout=5).json()
testing_response = requests.get(testing_url, timeout=5).json()
hospital_response = requests.get(hospital_url, timeout=5).json()
deaths_response = requests.get(deaths_url, timeout=5).json()
time_response = requests.get(time_url, timeout=5).json()

now_data = pd.DataFrame()
for i in range(len(cases_response['features'])):
    #Current total cases by zip code
    zip_code = cases_response['features'][i]['properties']['Zip']
    cases = cases_response['features'][i]['properties']['Count']
    if cases == '<10': cases = 10

    #Current rate per 100k population by zip code
    rate_per_100k = cases_response['features'][i]['properties']['Rate_per_100000']
    if rate_per_100k == 'Too few cases to report' or rate_per_100k == 'Zero cases': rate_per_100k = 'NaN'
    row = {'zip_code':zip_code, 'num_cases':cases, 'rate_per_100k': rate_per_100k}
    now_data = now_data.append(row, ignore_index=True)


#Current total deaths
deaths_response['features'][0]['properties']['Deaths_Total_Age']

time_data = pd.DataFrame()
for i in range(len(time_response['features'])):
    time_stamp = time_response['features'][i]['properties']['Date'].split(' ')[0]
    #Trajectory of cases over time
    new_cases = time_response['features'][i]['properties']['AC_Cases']
    cumul_cases = time_response['features'][i]['properties']['AC_CumulCases']

    #Trajectory of deaths over time
    new_deaths = time_response['features'][i]['properties']['AC_Deaths']
    cumul_deaths = time_response['features'][i]['properties']['AC_CumulDeaths']

    row = {'time_stamp':time_stamp, 'new_cases':new_cases, 'cumul_cases': cumul_cases, 'new_deaths': new_deaths, 'cumul_deaths': cumul_deaths}
    time_data = time_data.append(row, ignore_index=True)

test_data = pd.DataFrame()
for i in range(len(testing_response['features'])):
    time_stamp = testing_response['features'][i]['properties']['Date'].split(' ')[0]
    #Positive case rate
    positive_case_rate = 100*testing_response['features'][i]['properties']['Perc_Positive']
    
    #Number of tests per day
    num_tests = testing_response['features'][i]['properties']['Tests']

    row = {'time_stamp':time_stamp, 'positive_case_rate':positive_case_rate, 'num_tests': num_tests}
    test_data = test_data.append(row, ignore_index=True)

time_data = pd.merge(time_data, test_data, on='time_stamp', how='outer')
