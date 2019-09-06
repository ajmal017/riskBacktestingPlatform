import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import Flask

from config import basedir
from flask import request, jsonify
import flask_excel
from celery import Celery
# Celery configuration

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
flask_excel.init_excel(app)
# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


db = SQLAlchemy(app)
app.config.from_object('config')
lm = LoginManager()
lm.setup_app(app)
lm.login_view = 'login'



from app import views,models ,bar
