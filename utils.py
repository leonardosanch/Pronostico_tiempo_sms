
import pandas as pd
from twilio.rest import Client
from twilio_config import TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN,PHONE_NUMBER,API_KEY_WAPI
from datetime import datetime
import requests
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
from deep_translator import GoogleTranslator
import time



def get_date():

    input_date = datetime.now()
    input_date = input_date.strftime("%Y-%m-%d")

    return input_date

def request_wapi(api_key,query):

    url_clima = 'http://api.weatherapi.com/v1/forecast.json?key='+api_key+'&q='+query+'&days=1&aqi=no&alerts=no'

    try :
        response = requests.get(url_clima).json()
    except Exception as e:
        print(e)

    return response

def get_forecast(response,i):

    fecha = response['forecast']['forecastday'][0]['hour'][i]['time'].split()[0]
    hora = int(response['forecast']['forecastday'][0]['hour'][i]['time'].split()[1].split(':')[0])
    condicion = response['forecast']['forecastday'][0]['hour'][i]['condition']['text']
    tempe = response['forecast']['forecastday'][0]['hour'][i]['temp_c']
    rain = response['forecast']['forecastday'][0]['hour'][i]['will_it_rain']
    prob_rain = response['forecast']['forecastday'][0]['hour'][i]['chance_of_rain']

    return fecha,hora,condicion,tempe,rain,prob_rain

def create_df(data):

    col = ['Fecha','Hora','Condicion','Temperatura','Lluvia','prob_lluvia']
    df = pd.DataFrame(data,columns=col)
    df = df.sort_values(by = 'Hora',ascending = True)

    df_rain = df[(df['Lluvia']==1) & (df['Hora']>6) & (df['Hora']< 22)]
    df_rain = df_rain[['Hora','Condicion']]
    df_rain.set_index('Hora', inplace = True)

    return df_rain

def send_message(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, input_date, df, query):

    account_sid = TWILIO_ACCOUNT_SID
    auth_token = TWILIO_AUTH_TOKEN

    client = Client(account_sid, auth_token)

    # Traducir el DataFrame a español y formatear el mensaje
    df_spanish = df.copy()
    for index, row in df.iterrows():
        condition = row['Condicion']
        translated = GoogleTranslator(source='auto', target='es').translate(condition)
        df_spanish.at[index, 'Condicion'] = translated

    # Crear el mensaje con la información traducida
    message_body = f'\nHola!\n\nEl pronóstico de lluvia para hoy {input_date} en {query} es:\n\n'
    for index, row in df_spanish.iterrows():
        message_body += f'{index} {row["Condicion"]}\n'  # index es la hora

    # Enviar el mensaje usando Twilio
    message = client.messages \
                    .create(
                        body=message_body,
                        from_=PHONE_NUMBER,
                        to='+573006420645'
                    )

    return message.sid
