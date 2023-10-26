from azure.servicebus import QueueClient
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

app.secret_key = app.config.get('SECRET_KEY')

queue_client = QueueClient.from_connection_string(app.config.get('SERVICE_BUS_CONNECTION_STRING'),
                                                  app.config.get('SERVICE_BUS_QUEUE_NAME'))

db = SQLAlchemy(app)

from . import routes