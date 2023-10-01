from flask import Flask, render_template, request, Markup
import numpy as np
import pandas as pd
from utils.fertilizer import fertilizer_dic
import requests
import config
import pickle
import io
import torch
from torchvision import transforms
from PIL import Image

# Load crop recommendation model

crop_recommend_model_path = 'models/DecisionTree.pkl'
crop_recommend_model = pickle.load(open(crop_recommend_model_path, 'rb'))

# Custom functions for calculations
def weather_fetch(city_name):
    """
    Fetch and returns the temperature and humidity of a city
    :params: city_name
    :return: temperature, humidity
    """
    api_key = config.weather_api_key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()

    if x["cod"] != "404":
        y = x["main"]

        temp = round((y["temp"] - 273.15), 2)
        hum = y["humidity"]
        return temp, hum
    else:
        return None


app = Flask(__name__)


@ app.route('/')
def home():
    #front end render_templete()
    return "front end render_templete(homepage)"


@ app.route('/crop-recommend')
def crop_recommend():
    # get N,K,Ph , phlevels, rainflal , state and city
    return "front end render_templete(crop recommnedation form page)"


@ app.route('/fertilizer')
def fertilizer_recommendation():
    # title = 'Fertilizer Suggestion'

    # return render_template('fertilizer.html', title=title)
    pass







@ app.route('/crop-predict', methods=['POST'])
def crop_prediction():
    title = 'Crop Recommendation'

    if request.method == 'POST':
        # N2 = int(request.form['nitrogen'])
        # P2 = int(request.form['phosphorous'])
        # K2 = int(request.form['pottasium'])
        # ph = float(request.form['ph'])
        # rainfall = float(request.form['rainfall'])

        # city = request.form.get("city")
        data = request.get_json()
        
        N2 = int(data['nitrogen'])
        P2 = int(data['phosphorous'])
        K2 = int(data['pottasium'])
        ph = float(data['ph'])
        rainfall = float(data['rainfall'])
        city = data["city"]

        if weather_fetch(city) != None:
            try:
                temperature, humidity = weather_fetch(city)
                data = np.array([[N2, P2, K2, temperature, humidity, ph, rainfall]])
                my_predict = crop_recommend_model.predict(data)
                final_predict = my_predict[0]
                return final_predict
            # return render_template('crop-result.html', prediction=final_predict, title=title)
            except Exception as e:
                print(e)
                return "error"
        else:
            return "error with weather fetch "
            # return render_template('try_again.html', title=title)

# render fertilizer recommendation result page


@ app.route('/fertilizer-predict', methods=['POST'])
def fert_recommend():
    data = request.get_json()
    crop_name = str(data['cropname'])
    N1 = int(data['nitrogen'])
    P1 = int(data['phosphorous'])
    K1 = int(data['pottasium'])

    df = pd.read_csv('Data/fertilizer.csv')

    nr = df[df['Crop'] == crop_name]['N'].iloc[0]
    pr = df[df['Crop'] == crop_name]['P'].iloc[0]
    kr = df[df['Crop'] == crop_name]['K'].iloc[0]

    n = nr - N1
    p = pr - P1
    k = kr - K1
    temp = {abs(n): "N", abs(p): "P", abs(k): "K"}
    max_value = temp[max(temp.keys())]
    if max_value == "N":
        if n < 0:
            key = 'NHigh'
        else:
            key = "Nlow"
    elif max_value == "P":
        if p < 0:
            key = 'PHigh'
        else:
            key = "Plow"
    else:
        if k < 0:
            key = 'KHigh'
        else:
            key = "Klow"

    # response = Markup(str(fertilizer_dic[key]))
    response = fertilizer_dic[key]
    return response
    # return render_template('fertilizer-result.html', recommendation=response, title=title)



if __name__ == '__main__':
    app.run(debug=True)
