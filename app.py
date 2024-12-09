# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# Все выводы в функциях и блоках кода писал на английском, для проверки своих знаний в иностранном языке.
# Единственное - это комментарии сложных моментов, которые лучше объяснить по-русски для проверяющего
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# I wrote all the outputs in functions and code blocks in English to test my knowledge of a foreign language.
# The only thing is comments on difficult moments that are better explained in Russian for the examiner
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

from flask import Flask, request, render_template
import requests as rq

app = Flask(__name__)

API_key = 'Rg2Bp0Mxu9Lpz4uabYzfOZuEbrt1pKP9'

def get_location_key(city_name):
    url = f'http://dataservice.accuweather.com/locations/v1/cities/search?apikey={API_key}&q={city_name}&language=en-us'
    resp = rq.get(url)
    if resp.status_code == 200 and resp.json():
        return resp.json()[0]['Key']
    return None

def get_weather_data(location_key):
    url = f'http://dataservice.accuweather.com/currentconditions/v1/{location_key}?apikey={API_key}&language=en-us'
    resp = rq.get(url)
    if resp.status_code == 200:
        return resp.json()[0]
    return None

def check_bad_weather(temp, prec_prob):
    # По умолчанию мы считаем, что погода плохая, поэтому
    # при ошибочных данных будем возвращать плохую погоду

    if temp < -20 or temp > 30:
        return {'is_bad': True, 'reason': 'extreme temperature'}
    
    # При проверке проекта я заметил, что не могу получить значение
    # скорости ветра, поэтому часть кода закомменитрованна. При этом, 
    # если бы были данные о ветре, то код работал бы исправно
    # if w_speed < 0 or w_speed > 400:
    #     return {'is_bad': True, 'reason': 'bad or none value of wind speed'}
    # if w_speed > 50:
    #     return {'is_bad': True, 'reason': 'strong wind'}

    if prec_prob > 100 or prec_prob < 0:
        return {'is_bad': True, 'reason': 'bad or none value of precipitation probability'}
    if prec_prob > 70:
        return {'is_bad': True, 'reason': 'high probability of precipitation'}
    
    return {'is_bad': False, 'reason': 'Weather is good'}

@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_city = request.form['start_city']
        start_weather = get_weather_data(get_location_key(start_city))

        end_city = request.form['end_city']
        end_weather = get_weather_data(get_location_key(end_city))

        if start_weather and end_weather:
            try:
                start_temp = start_weather.get('Temperature', {}).get('Metric', {}).get('Value', -21)
                # Если данных нет, то считаем, что погода плохая
                # start_wind_speed = start_weather.get('Wind', {}).get('Metric', {}).get('Value', -1)
                start_precipitation_prob = 100 if start_weather.get('HasPrecipitation') else 0
                start_condition_text = start_weather.get('WeatherText', 'No data')

                start_condition = check_bad_weather(start_temp, start_precipitation_prob)

                end_temp = end_weather.get('Temperature', {}).get('Metric', {}).get('Value', -21)
                # Если данных нет, то считаем, что погода плохая
                # end_wind_speed = end_weather.get('Wind', {}).get('Metric', {}).get('Value', -1)
                end_precipitation_prob = 100 if end_weather.get('HasPrecipitation') else 0
                end_condition_text = end_weather.get('WeatherText', 'No data')

                end_condition = check_bad_weather(end_temp, end_precipitation_prob)

                return render_template(
                    'output.html',
                    start_condition = f'{'Bad weather - ' if start_condition['is_bad'] else ''}{start_condition['reason']}',
                    end_condition = f'{'Bad weather - ' if end_condition['is_bad'] else ''}{end_condition['reason']}',
                    start_condition_text = start_condition_text,
                    end_condition_text = end_condition_text
                )

            except KeyError as error:
                error_msg = f'Error with weather data: {error}'
                return render_template('index.html', error = error_msg)
            
        else:
            error_msg = 'Error with weather data: Please, check the city names.'
            return render_template('index.html', error = error_msg)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug = True)