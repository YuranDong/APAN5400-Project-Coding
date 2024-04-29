import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import urllib.parse
from sqlalchemy import create_engine
from pymongo import MongoClient

matplotlib.use('Agg')
sns.set_theme()


def connect_to_postgresql():
    """
    connect to postgresql database
    :return: the engine for sql connection
    """
    # database parameter
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


def connect_to_mongodb():
    """
    connect to postgresql database
    :return: the collection for mongodb to do query
    """
    # database parameter
    host = 'localhost'
    port = 27017
    db_name = 'airbnb'
    collection_name = 'reviews'

    client = MongoClient(host, port)
    db = client[db_name]  # database
    collection = db[collection_name]  # collection
    return collection


def query_property_id(property_id, engine):
    """
    query for property features through property_id
    :param property_id: integer
    :param engine: Postresql query engine
    :return: pandas dataframe
    """
    # Define SQL query
    sql_query = f'''
    select
        name
        -- location info
        ,neighbourhood_cleansed
        ,city
        ,state
        -- property info
        ,property_type
        ,room_type
        ,accommodates
        ,bathrooms
        ,bedrooms
        ,beds
        ,price
        -- review info
        ,number_of_reviews
        ,review_scores_rating
        ,review_scores_accuracy
        ,review_scores_cleanliness
        ,review_scores_checkin
        ,review_scores_communication
        ,review_scores_location
        ,review_scores_value
    from properties
    where id = {property_id}
    '''
    # Load data into a DataFrame
    dataframe = pd.read_sql(sql_query, engine)

    # if property id does not exist
    if dataframe.empty:
        output = pd.DataFrame({'property_id': ['No Data Found']})
        return output
    else:
        # adjust dataframe
        output = dataframe.T
        output.reset_index(inplace=True)
        output.columns = ['features', 'values']
        return output


def query_property_word(property_id, review_word, collection):
    """
    Queries the most recent 10 reviews for certain property
    :param property_id: Int the property id
    :param review_word: Str, the words to be searched for in the reviews
    :param collection: The MongoDB collection
    :return:pd.DataFrame
    """
    # define text searching rules (case-insensitive)
    query_rule = {'listing_id': str(property_id), 'comments': {'$regex': review_word, '$options': 'i'}}
    sort_rule = [('date', -1)]

    # query
    reviews = collection.find(query_rule).sort(sort_rule).limit(10)

    # output result
    df = pd.DataFrame(list(reviews))
    if df.empty:
        output = pd.DataFrame({'reviews': ['No Data Found']})
        return output
    else:
        df.drop(['_id', 'reviewer_id', 'state', 'city', 'data_date'], axis=1, inplace=True)
        return df


def get_neighborhood_list(engine):
    """
    get a list of all city for drop down box
    :param engine: Postresql query engine
    :return: List[str] list containing all city available in database
    """
    sql_query = f'''
            SELECT *
            FROM neighbourhood
            ORDER BY state,city,neighbourhood_cleansed
        '''

    dataframe = pd.read_sql(sql_query, engine)
    dataframe['state'] = dataframe['state'].str.upper()
    dataframe['neighbourhood_city_state'] = dataframe['neighbourhood_cleansed'] + ', ' + dataframe['city'] + ', ' + \
                                            dataframe['state']
    returned_list = list(dataframe['neighbourhood_city_state'])
    return returned_list


def get_city_list(engine):
    """
    get a list of all city for drop down box
    :param engine: Postresql query engine
    :return: List[str] list containing all city available in database
    """
    sql_query = f'''
        select * from city
        '''
    dataframe = pd.read_sql(sql_query, engine)
    dataframe['state'] = dataframe['state'].str.upper()
    dataframe['city_state'] = dataframe['city'] + ', ' + dataframe['state']
    returned_list = list(dataframe['city_state'])

    return returned_list


def get_neighborhood_details(name, engine):
    """
    get the total listing number of a certain neighbourhood
    :param name: str, the name of the combination of neighbourhood city and state
    :param engine: Postgresql query engine
    :return: pandas.DataFrame
    """

    selected_neighbourhood = name.split(', ')[0].strip()
    selected_city = name.split(', ')[1].strip()
    selected_state = name.split(', ')[2].strip().lower()

    sql_query = f"""
    SELECT *
    FROM neighbourhood
    WHERE neighbourhood_cleansed = '{selected_neighbourhood}' AND city = '{selected_city}' AND state = '{selected_state}'
    """

    dataframe = pd.read_sql(sql_query, engine)
    return dataframe


def get_city_details(name, engine):
    """
    get the total listing number of a certain city
    :param name: str, the name of the combination of city and state
    :param engine: Postgresql query engine
    :return: pandas.DataFrame
    """
    selected_city = name.split(', ')[0].strip()
    selected_state = name.split(', ')[1].strip().lower()

    sql_query = f"""
    SELECT *
    FROM city
    WHERE city = '{selected_city}' AND state = '{selected_state}'
    """

    dataframe = pd.read_sql(sql_query, engine)
    return dataframe


def get_plots_neighbourhood(name, engine):
    """
    draw some plot for a certain neighbourhood
    :param name: str, the name of the combination of neighbourhood city and state
    :param engine: Postgresql query engine
    :return: List[str] the list of plots
    """
    # clean the name
    selected_neighbourhood = name.split(',')[0].strip()
    selected_city = name.split(', ')[1].strip()
    selected_state = name.split(', ')[2].strip().lower()

    # the collection of the url of all the plots
    plots = []

    # get first data
    sql_query = f"""
    SELECT *
    FROM properties
    WHERE neighbourhood_cleansed = '{selected_neighbourhood}' AND city = '{selected_city}' AND state = '{selected_state}'
    """
    dataframe = pd.read_sql(sql_query, engine)
    dataframe['price'] = pd.to_numeric(dataframe['price'], errors='coerce')

    # plot for the distribution of price
    # remove outlier (price higher than 5000 per day)
    filtered_df = dataframe[dataframe['minimum_nights'] <= 5000]
    plt.figure()
    sns.histplot(data=filtered_df, x='price', bins=40, kde=True)  # kde adds a density curve
    plt.title("Distribution of Property Prices")
    plt.xlabel("Price (Outlier Removed)")
    plt.ylabel("Frequency")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)
    plots.append(uri)

    # plot for the Room types
    plt.figure()
    sns.countplot(data=dataframe, x='room_type')
    plt.title("Room Type Distribution")
    plt.xlabel("Room Type")
    plt.ylabel("Count")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)
    plots.append(uri)

    # plot for the minimum nights
    # ignore outlier (above 1 year)
    filtered_df2 = dataframe[(dataframe['minimum_nights'] >= 0) & (dataframe['minimum_nights'] <= 365)]
    plt.figure()
    sns.histplot(data=filtered_df2, x='minimum_nights', bins=40, kde=True)
    plt.title("Distribution of Minimum Nights")
    plt.xlabel("Minimum Nights (Outlier Removed)")
    plt.ylabel("Frequency")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)
    plots.append(uri)

    # plot for the Avg price fluctuation and Renting out rate for next year
    # get second data
    sql_query = f"""
    SELECT 
        date
        ,occupancy_rate
        ,avg_price
    FROM order_info_by_neighbourhood
    WHERE neighbourhood_cleansed = '{selected_neighbourhood}' AND city = '{selected_city}' AND state = '{selected_state}'
    """
    dataframe2 = pd.read_sql(sql_query, engine)

    # plot for Empty Rate Over Time
    plt.figure()
    sns.lineplot(data=dataframe2, x='date', y='occupancy_rate', marker='o')
    plt.title("Empty Rate Over Time")
    plt.xlabel("Date")
    plt.ylabel("Empty Rate (%)")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)
    plots.append(uri)

    # plot for avg price Over Time
    plt.figure()
    sns.lineplot(data=dataframe2, x='date', y='avg_price', marker='o')
    plt.title("Average Price Over Time")
    plt.xlabel("Date")
    plt.ylabel("Average Price ($)")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)
    plots.append(uri)

    return plots


def get_plots_city(name, engine):
    """
    draw some plot for a certain neighbourhood
    :param name: str, the name of the combination of neighbourhood city and state
    :param engine: Postgresql query engine
    :return: List[str] the list of plots
    """
    # clean the name
    selected_city = name.split(', ')[0].strip()
    selected_state = name.split(', ')[1].strip().lower()

    # the collection of the url of all the plots
    plots = []

    # get first data
    sql_query = f"""
    SELECT *
    FROM properties
    WHERE city = '{selected_city}' AND state = '{selected_state}'
    """
    dataframe = pd.read_sql(sql_query, engine)
    dataframe['price'] = pd.to_numeric(dataframe['price'], errors='coerce')

    # plot for the distribution of price
    # remove outlier (price higher than 5k per day)
    filtered_df = dataframe[dataframe['minimum_nights'] <= 5000]
    plt.figure()
    sns.histplot(data=filtered_df, x='price', bins=40, kde=True)  # kde adds a density curve
    plt.title("Distribution of Property Prices")
    plt.xlabel("Price (Outlier Removed)")
    plt.ylabel("Frequency")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)
    plots.append(uri)

    # plot for the Room types
    plt.figure()
    sns.countplot(data=dataframe, x='room_type')
    plt.title("Room Type Distribution")
    plt.xlabel("Room Type")
    plt.ylabel("Count")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)
    plots.append(uri)

    # plot for the minimum nights
    # ignore outlier (above 1 year)
    filtered_df2 = dataframe[(dataframe['minimum_nights'] >= 0) & (dataframe['minimum_nights'] <= 365)]
    plt.figure()
    sns.histplot(data=filtered_df2, x='minimum_nights', bins=40, kde=True)
    plt.title("Distribution of Minimum Nights")
    plt.xlabel("Minimum Nights (Outlier Removed)")
    plt.ylabel("Frequency")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)
    plots.append(uri)

    # plot for the Avg price fluctuation and Renting out rate for next year
    # get second data
    sql_query = f"""
    SELECT 
        date
        ,occupancy_rate
        ,avg_price
    FROM order_info_by_city
    WHERE city = '{selected_city}' AND state = '{selected_state}'
    """
    dataframe2 = pd.read_sql(sql_query, engine)

    # plot for Empty Rate Over Time
    plt.figure()
    sns.lineplot(data=dataframe2, x='date', y='occupancy_rate', marker='o')
    plt.title("Empty Rate Over Time")
    plt.xlabel("Date")
    plt.ylabel("Empty Rate (%)")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)
    plots.append(uri)

    # plot for avg price Over Time
    plt.figure()
    sns.lineplot(data=dataframe2, x='date', y='avg_price', marker='o')
    plt.title("Average Price Over Time")
    plt.xlabel("Date")
    plt.ylabel("Average Price ($)")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)
    plots.append(uri)

    return plots
