import os

from dotenv import load_dotenv

load_dotenv()

LOGIN = os.getenv('LOGIN')
PASS = os.getenv('PASS')
DB_NAME = os.getenv('DB_NAME')
HOST = os.getenv('HOST')
TOKEN = os.getenv('TOKEN')

