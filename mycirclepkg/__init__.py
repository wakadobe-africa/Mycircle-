import os

from flask import Flask
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from instance.config import SQLALCHEMY_DATABASE_URI
from mycirclepkg.config import TestConfig,LiveConfig
from mycirclepkg.model import db

csrf= CSRFProtect()
def create_app():
    from mycirclepkg.model import db
    app=Flask(__name__, instance_relative_config=True)

    app.config.from_pyfile('config.py')
    app.config.from_object(LiveConfig)
    app.config['SQLALCHEMY_DATABASE_URI']= os.getenv('SQLALCHEMY_DATABASE_URI')
    db.init_app(app)
    migrate = Migrate(app,db)
    csrf.init_app(app)
    return app

app = create_app()

from mycirclepkg import user_form,user_routes,devadmin_routes