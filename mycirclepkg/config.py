import os
from dotenv import load_dotenv

load_dotenv()

class General(object):
    APP_NAME = 'MYCircle'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI',
        'mysql+mysqlconnector://root@localhost/mycircledb'
    )

class LiveConfig(General):
    DATABASE = os.getenv('DB_NAME', 'mycircledb')
    # Only set SECRET_KEY from env var if it is explicitly provided.
    # In local dev the instance/config.py file supplies it instead.
    if os.getenv('SECRET_KEY'):
        SECRET_KEY = os.environ['SECRET_KEY']

class TestConfig(General):
    DATABASE = os.getenv('DB_NAME', 'mycircledb')