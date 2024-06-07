import requests
from twilio.rest import Client
import sqlite3
import time

# Configurações da API do OpenWeatherMap
WEATHER_API_KEY = '6a57de91e561837e951718bdeb71b315'

# Configurações da API Twilio
TWILIO_ACCOUNT_SID = 'YOUR_TWILIO_ACCOUNT_SID'
TWILIO_AUTH_TOKEN = 'YOUR_TWILIO_AUTH_TOKEN'
TWILIO_PHONE_NUMBER = 'YOUR_TWILIO_PHONE_NUMBER'

# Configurações do banco de dados SQLite
DATABASE_FILE = 'users.db'

# Função para criar a tabela de usuários
def create_user_table():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Função para adicionar usuário
def add_user(name, email, phone, latitude, longitude):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO users (name, phone, latitude, longitude)
    VALUES (?, ?, ?, ?)
    ''', (name, email, phone, latitude, longitude))
    conn.commit()
    conn.close()

# Função para obter todos os usuários
def get_all_users():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT name, phone, latitude, longitude FROM users')
    users = cursor.fetchall()
    conn.close()
    return users

# Função para obter dados de alertas climáticos
def get_weather_alerts(place):
    try:
        place = place.replace(" ", "")
        response = requests.get(f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{place}?unitGroup=us&key=TX3ZE8JKKPSXWVAE37EYP9XNC&contentType=json&include=current,alerts')
        res = response.json()
        return res['resolvedAddress'], res['alerts']
    except:
        return None, None


# Função para verificar risco de inundação
def check_flood_alerts(alerts_data):
    for alert in alerts_data:
        if 'flood' in alert['event'].lower():
            return True
    return False

# Função para enviar SMS
def send_sms(phone_number, message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number
    )

# Função principal
def main():
    create_user_table()
    
    while True:
        # users = get_all_users()
        users = [['hugo', '231','rio de janeiro'] , ['mari', '1212312', 'governador valladares']]

        for name, phone, location in users:
            print(location)
            place, alerts_data = get_weather_alerts(location)
            if place == None:
                continue
            if check_flood_alerts(alerts_data):
                message = f"Alerta de inundação para sua área! Por favor, tome as devidas precauções. - Alerta Maré Cheia"
                send_sms(phone, message)
                print(f"Enviado alerta para {name} - ({phone})")
            else:
                print(f"Nenhum alerta para {place}")
        time.sleep(15 * 60)

if __name__ == '__main__':
    main()
