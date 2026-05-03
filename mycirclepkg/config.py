import os


class General(object):
    APP_NAME='MYCircle'
    SQLALCHEMY_DATABASE_URI=os.getenv('SQLALCHEMY_DATABASE_URI')
    SECRET_KEY=os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATION=False
class LiveConfig(General):
    DATABASE = 'mycircledb'
    
class TestConfig(General):
    DATABASE='mycircledb'