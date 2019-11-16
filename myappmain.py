from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate

app = Flask(__name__, template_folder="templates")
app.config.from_pyfile('config.py')
CORS(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
