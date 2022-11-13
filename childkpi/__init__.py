from childkpi.creds import creds
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{creds["user"]}:{creds["pass"]}@{creds["host"]}:{creds["port"]}/{creds["dbname"]}'
application.config['SECRET_KEY'] = '62b9e7e20ba41ca4d119bf39'
db = SQLAlchemy(app)
app.app_context().push()
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = 'info'

from childkpi import routes