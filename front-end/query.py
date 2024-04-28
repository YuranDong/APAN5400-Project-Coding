import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import urllib.parse
from sqlalchemy import create_engine

def connect_to_postgresql():
    # Replace these values with your database connection details
    username = 'postgres'
    password = '123'
    host = 'localhost'
    port = '5432'
    dbname = 'airbnb'

    # Create the connection string
    connection_string = f"postgresql://{username}:{password}@{host}:{port}/{dbname}"

    # Create the database engine
    engine = create_engine(connection_string)

    return engine

def query_property_id(property_id,engine):
    '''
    query for property features through property_id
    :param property_id: integer
    :param engine: Postresql query engine
    :return: pandas dataframe
    '''
    # Define SQL query
    sql_query = f'''
    select
        name
        ,neighbourhood_cleansed
        ,room_type
    from properties
    where id = {property_id}
    '''
    # Load data into a DataFrame
    dataframe = pd.read_sql(sql_query, engine)
    return dataframe
    # db = [
    #     pd.DataFrame({'name': 'Cozy Cottage', 'location': '123 Maple Street', 'price': '250,000 USD'}, index=[0]),
    #     pd.DataFrame({'name': 'Urban Flat', 'location': '456 City Ave', 'price': '350,000 USD'}, index=[0]),
    #     pd.DataFrame({'name': 'Beach House', 'location': '789 Ocean Blvd', 'price': '750,000 USD'}, index=[0])
    # ]
    # # keep in mind that return a null value if property id not found
    # return db[property_id-1]

def query_property_word(review_word):
    ########################################################################################
    # input: review_word (string)
    # output: dataframe containing top n / most recent n reviews that contains given word (dataframe)
    # usage: query for specific word for database's review session
    db = [
        pd.DataFrame({'name': 'Cozy Cottage', 'location': '123 Maple Street', 'price': '250,000 USD'}, index=[0]),
        pd.DataFrame({'name': 'Urban Flat', 'location': '456 City Ave', 'price': '350,000 USD'}, index=[0]),
        pd.DataFrame({'name': 'Beach House', 'location': '789 Ocean Blvd', 'price': '750,000 USD'}, index=[0])
    ]
    # keep in mind that return a null value if word not found / incomplete
    return db[1]


def get_neighborhood_list(database):
    ########################################################################################
    # input: database or nothing
    # output: list containing all neighborhood available in database (list)
    # usage: get a list of all neighborhood for drop down box

    # keep in mind that return a null value if word not found / incomplete
    return ['Maplewood', 'Lakeview', 'Downtown']

def get_city_list(database):
    ########################################################################################
    # input: database or nothing
    # output: list containing all city available in database (list)
    # usage: get a list of all city for drop down box

    # keep in mind that return a null value if word not found / incomplete
    return ['Maplewood', 'Lakeview', 'Downtown']

def get_neighborhood_details(name):
    ########################################################################################
    # input: selected neighborhood name (string)
    # output: dataframe containing features of selected neighborhood (dataframe)
    # usage: query for specific word for database's review session
    details = [
        pd.DataFrame({'name': 'Maplewood', 'location': '123 Maple Street', 'price': '250,000 USD'}, index=[0]),
        pd.DataFrame({'name': 'Lakeview', 'location': '456 City Ave', 'price': '350,000 USD'}, index=[0]),
        pd.DataFrame({'name': 'Downtown', 'location': '789 Ocean Blvd', 'price': '750,000 USD'}, index=[0])
    ]
    for detail in details:
        if detail['name'][0] == name:
            return detail
    # keep in mind that return a null value if word not found / incomplete like below
    return pd.DataFrame({'name': ['Not Found'], 'location': ['N/A'], 'price': ['N/A']})

def get_city_details(name):
    ########################################################################################
    # input: selected city name (string)
    # output: dataframe containing features of selected city (dataframe)
    # usage: query for specific word for database's review session
    details = [
        pd.DataFrame({'name': 'Maplewood', 'location': '123 Maple Street', 'price': '250,000 USD'}, index=[0]),
        pd.DataFrame({'name': 'Lakeview', 'location': '456 City Ave', 'price': '350,000 USD'}, index=[0]),
        pd.DataFrame({'name': 'Downtown', 'location': '789 Ocean Blvd', 'price': '750,000 USD'}, index=[0])
    ]
    for detail in details:
        if detail['name'][0] == name:
            return detail
    # keep in mind that return a null value if word not found / incomplete like below
    return pd.DataFrame({'name': ['Not Found'], 'location': ['N/A'], 'price': ['N/A']})

def get_plots(name):
    ########################################################################################
    # input: selected neighborhood (string)
    # output: lists of plots that we want to show in dashboard (list)
    # usage: get the plots / visualizations from database

    df = pd.DataFrame({
        'x': range(10),
        'y': np.random.randint(0, 100, 10),
        'group': [10]*10
    })

    plots = []
    for i in range(1, 4):
        plt.figure()
        plt.plot(df['x'], df['y'] * i)
        plt.title(f'Plot {i}')
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = 'data:image/png;base64,' + urllib.parse.quote(string)
        plots.append(uri)

    return plots