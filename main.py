import tkinter as tk
import requests
import hashlib

def check_data():
    email = email_entry.get()
    password = password_entry.get()
    hashed_password = hashlib.sha1(password.encode()).hexdigest()
    data = {"email": email, "password": hashed_password}
    response = requests.post('https://example.com/check', json=data)
    result_label.config(text=response.json().get("result"))

app = tk.Tk()
app.title("Проверка утечки данных")

tk.Label(app, text="E-mail или логин:").pack()
email_entry = tk.Entry(app)
email_entry.pack()

tk.Label(app, text="Пароль:").pack()
password_entry = tk.Entry(app, show="*")
password_entry.pack()

tk.Button(app, text="Проверить", command=check_data).pack()
result_label = tk.Label(app, text="")
result_label.pack()

app.mainloop()
