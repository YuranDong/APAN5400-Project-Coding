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
from query import *

app = Flask(__name__)

@app.route('/')
# general welcome webpage with three buttons that are accessible for additional webpages
def welcome():
    return render_template('welcome.html')

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
