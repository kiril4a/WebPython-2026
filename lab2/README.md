# Лабораторна робота 2: FastAPI + PostgreSQL

## Опис проекту
У цій лабораторній роботі здійснено міграцію системи  `ІС «Стоматологічний кабінет»` з локальної бази SQLite (створеної у ЛР 1) на повноцінну реляційну СУБД **PostgreSQL**, використовуючи `psycopg2` як драйвер та **SQLAlchemy** як ORM. 

Всі CRUD-операції, валідації та логіка серверного рендерингу (Jinja2) повністю збережені, але тепер дані надійно зберігаються на віддаленій / локальній СКБД Postgres.

## Фрагмент ключового коду (database.py)
```python
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost/clinic_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

## Скріншоти результату
![Результат 1](image.png)
![Результат 2](image2.png)