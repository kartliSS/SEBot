import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
admin_id = int(os.getenv("ADMIN_ID"))

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
