class General(object):
    APP_NAME='MYCircle'
    SQLALCHEMY_TRACK_MODIFICATION=False
class LiveConfig(General):
    DATABASE = 'mycircledb'
    
class TestConfig(General):
    DATABASE='mycircledb'