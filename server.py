import requests
import hashlib
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import threading
import psycopg2
import uuid
from sqlalchemy import or_

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для клиента


conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="project",
    user="main",
    password="123"
)

# Подключение к PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://main:123@localhost:5432/project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Модель данных
class DataLeak(db.Model):
    __tablename__ = "adress"
    id = db.Column(db.String(36), primary_key=True)
    email = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    leaked_data = db.Column(db.Text)


# Функция для проверки email через API Have I Been Pwned, но пока не работает по причине "у меня нет денег"
#def check_email_leak(email):
    #url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
    #headers = {
        #"User-Agent": "Python Client",
        #"hibp-api-key": "тут будет ключ, жопой клянусь"
    #}
    #response = requests.get(url, headers=headers)
    #return response.json() if response.status_code == 200 else None

# Функция для проверки пароля через PwnedPasswords API, это, благо, бесплатно работает
def check_password_leak(password):
    sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    first_5_chars = sha1_hash[:5]
    remaining_chars = sha1_hash[5:]

    url = f"https://api.pwnedpasswords.com/range/{first_5_chars}"
    response = requests.get(url)
    if response.status_code == 200:
        hashes = response.text.splitlines()
        for hash_entry in hashes:
            if ":" not in hash_entry:
                continue
            hash_value, count = hash_entry.split(':')
            if hash_value == remaining_chars:
                return int(count)  # Возвращаем количество утечек
    return 0  # Если утечек не найдено


def save_leak_to_db(email=None, username=None, password=None, leaked_data=""):
    try:
        leak = DataLeak(
            id=str(uuid.uuid4()),
            email=email,
            username=username,
            password=password,
            leaked_data=leaked_data
        )
        db.session.add(leak)
        db.session.commit()
    except Exception as e:
        print("Ошибка при сохранении в бд:", e)

# API для проверки утечек
@app.route('/check', methods=['POST'])
def check_leak():
    data = request.json  # Получаем данные из запроса (email, username, password)
    email = data.get('email') or None
    username = data.get('username') or None
    password = data.get('password') or None


    filters = []
    if email:
        filters.append(DataLeak.email == email)
    if username:
        filters.append(DataLeak.username == username)
    if password:
        filters.append(DataLeak.password == password)


    leak_info = DataLeak.query.filter(or_(*filters)).first() if filters else None
    if leak_info:
        return jsonify({"status": "leaked", "details": leak_info.leaked_data})


    # Проверка email через Have I Been Pwned API
    #email_leak = check_email_leak(email)
    #if email_leak:
        #return jsonify({"status": "leaked", "details": f"Email {email} найден в утечках!"})

    # Проверка пароля через PwnedPasswords API
    if password:
        password_leak_count = check_password_leak(password)
        if password_leak_count > 0:
            print()
            save_leak_to_db(email=email, username=username, password=password)
            return jsonify({"status": "leaked", "details": f"Пароль найден в {password_leak_count} утечках!"})
    return jsonify({"status": "safe"})

# Запуск сервера в многопоточном режиме
def run_server():
    app.run(host='0.0.0.0', port=5000, threaded=True)


if __name__ == '__main__':
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

