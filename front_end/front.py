# import libraries
from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import urllib.parse

app = Flask(__name__)

@app.route('/')
# general welcome webpage with three buttons that are accessible for additional webpages
def welcome():
    return render_template('welcome.html')

def query_property_id(property_id):
    ######################################################################################## 
    # input: property_id (integer)
    # output: dataframe
    # usage: query for property features through property_id
    db = [
        pd.DataFrame({'name': 'Cozy Cottage', 'location': '123 Maple Street', 'price': '250,000 USD'}, index=[0]),
        pd.DataFrame({'name': 'Urban Flat', 'location': '456 City Ave', 'price': '350,000 USD'}, index=[0]),
        pd.DataFrame({'name': 'Beach House', 'location': '789 Ocean Blvd', 'price': '750,000 USD'}, index=[0])
    ]
    # keep in mind that return a null value if property id not found
    return db[property_id-1]

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

# navigation to property webpage
@app.route('/property', methods=['GET', 'POST'])
def property():
    if request.method == "POST":
        property_id = int(request.form['property_id'])
        property_data = query_property_id(property_id)
        
        review_word = request.form['review_word']
        review_data = query_property_word(review_word)
        operation = request.form['operation']
        if operation == 'REVIEW':
            # return render_template('review_result.html', property=review_data.to_html(index=False))
            # use 111111 since not available for review data
            return "111111"
        else:
            return render_template('property_result.html', property=property_data.to_html(index=False))
    return render_template('property.html')

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

# navigation to neighborhood webpage
@app.route('/neighborhood', methods=['GET', 'POST'])
def neighborhood():
    neighborhoods  = get_neighborhood_list(1)
    if request.method == 'POST':
        selected_neighborhood = request.form['neighborhood']
        details = get_neighborhood_details(selected_neighborhood)
        plots = get_plots(1)
        return render_template('neighborhood.html', neighborhoods=neighborhoods, details=details.to_html(index=False), selected_neighborhood=selected_neighborhood, plots = plots)
    return render_template('neighborhood.html', neighborhoods=neighborhoods, details=None, plots = None)

# navigation to city webpage
@app.route('/city', methods=['GET', 'POST'])
def city():
    cities  = get_city_list(1)
    if request.method == 'POST':
        selected_city = request.form['city']
        details = get_city_details(selected_city)
        plots = get_plots(1)
        return render_template('city.html', cities=cities, details=details.to_html(index=False), selected_city=selected_city, plots = plots)
    return render_template('city.html', cities=cities, details=None, plots = None)

if __name__ == '__main__':
    app.run(debug=True)
