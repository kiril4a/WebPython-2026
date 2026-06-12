# ЛР7 Flask

Запуск:

```powershell
cd lab7
pip install -r requirements.txt
python run.py
```

Адреса:

```text
http://127.0.0.1:5000/
```

Демо-користувачі:

```text
admin / admin
petrenko / 1234
shevchenko / 1234
```

Налаштування Gmail SMTP:

1. Скопіювати `lab7/.env.example` у `lab7/.env`.
2. У файлі `lab7/.env` замінити `MAIL_USERNAME`, `MAIL_PASSWORD` і `MAIL_DEFAULT_SENDER` на свої дані.
3. Запустити застосунок командою `python run.py`.

Приклад змінних:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your.email@gmail.com
MAIL_PASSWORD=your_google_app_password
MAIL_DEFAULT_SENDER=your.email@gmail.com
```

Важливо: для Gmail потрібно використовувати не звичайний пароль від акаунта, а Google App Password.

Автоматичні міграції:

```powershell
flask --app run.py db init
flask --app run.py db migrate -m "initial"
flask --app run.py db upgrade
```
