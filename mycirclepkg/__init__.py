from flask import Flask
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from mycirclepkg.config import TestConfig,LiveConfig
from mycirclepkg.model import db

csrf= CSRFProtect()
def create_app():
    from mycirclepkg.model import db
    app=Flask(__name__, instance_relative_config=True)

    # Load instance/config.py when present (local dev).  Use silent=True so
    # the app can start in production without a local file.
    app.config.from_pyfile('config.py', silent=True)
    # Apply class-based config last; env-var values win over the file.
    app.config.from_object(LiveConfig)

    db.init_app(app)
    migrate = Migrate(app,db)
    csrf.init_app(app)
    return app

app = create_app()

from mycirclepkg import user_form,user_routes,devadmin_routes