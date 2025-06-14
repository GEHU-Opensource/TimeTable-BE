import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from icecream import ic
import subprocess


# Load environment variables from .env file
load_dotenv()
db_name = os.getenv("POSTGRES_NAME")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", "5432")

try:
    conn = psycopg2.connect(
        dbname="postgres", user=user, password=password, host=host, port=port
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
    exists = cur.fetchone()

    if not exists:
        cur.execute(f'CREATE DATABASE "{db_name}"')
        print(f"Database '{db_name}' created.")
    else:
        print(f"Database '{db_name}' already exists.")

    cur.close()
    conn.close()

except Exception as e:
    print(f" Error: {e}")



# Run Django migrate
subprocess.run(["python", "manage.py", "migrate"], check=True)


# Create superuser non-interactively (values must be set in .env)
su_name = os.getenv("DJANGO_SU_NAME")
su_email = f"{os.getenv('DJANGO_SU_EMAIL')}@{os.getenv('CLIENT_EMAIL_DOMAIN')}"
su_password = os.getenv("DJANGO_SU_PASSWORD")


if su_name and su_email and su_password:
    subprocess.run([
        "python", "manage.py", "shell", "-c",
        (
            "from django.contrib.auth import get_user_model; "
            "User = get_user_model(); "
            "User.objects.filter(username='%s').exists() or "
            "User.objects.create_superuser('%s', '%s', '%s')" %
            (su_name, su_name, su_email, su_password)
        )
    ], check=True)
else:
    print("Superuser not created. Missing DJANGO_SU_NAME / DJANGO_SU_EMAIL / DJANGO_SU_PASSWORD in .env")