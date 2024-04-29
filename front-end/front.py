from flask import Flask, render_template, request
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
        review_word = request.form['review_word']
        operation = request.form['operation']

        if operation == 'REVIEW':
            review_data = query_property_word(property_id, review_word, collection=collection)
            return render_template('review_result.html', property=review_data.to_html(index=False))
        else:
            property_data, host_data = query_property_id(property_id, engine=engine)
            return render_template('property_result.html', property=property_data.to_html(index=False),
                                   host=host_data.to_html(index=False))
    return render_template('property.html')


# navigation to neighborhood webpage
@app.route('/neighborhood', methods=['GET', 'POST'])
def neighborhood():
    neighborhoods = get_neighborhood_list(engine=engine)
    if request.method == 'POST':
        selected_neighborhood = request.form['neighborhood']
        details = get_neighborhood_details(selected_neighborhood, engine=engine)
        plots = get_plots_neighbourhood(selected_neighborhood, engine=engine)
        return render_template('neighborhood.html', neighborhoods=neighborhoods, details=details.to_html(index=False),
                               selected_neighborhood=selected_neighborhood, plots=plots)
    return render_template('neighborhood.html', neighborhoods=neighborhoods, details=None, plots=None)


# navigation to city webpage
@app.route('/city', methods=['GET', 'POST'])
def city():
    cities = get_city_list(engine=engine)
    if request.method == 'POST':
        selected_city = request.form['city']
        details = get_city_details(selected_city, engine=engine)
        plots = get_plots_city(selected_city, engine=engine)
        return render_template('city.html', cities=cities, details=details.to_html(index=False),
                               selected_city=selected_city, plots=plots)
    return render_template('city.html', cities=cities, details=None, plots=None)


if __name__ == '__main__':
    engine = connect_to_postgresql()
    collection = connect_to_mongodb()
    app.run(debug=True)
