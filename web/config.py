import os

app_dir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    DEBUG = True
    POSTGRES_URL = os.getenv('TECHCONF_DB_URL')
    POSTGRES_USER = os.getenv('TECHCONF_DB_USER')
    POSTGRES_PW = os.getenv('TECHCONF_DB_PW')
    POSTGRES_DB = os.getenv('TECHCONF_DB_NAME')
    DB_URL = 'postgresql://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,
                                                          pw=POSTGRES_PW,
                                                          url=POSTGRES_URL,
                                                          db=POSTGRES_DB)
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI') or DB_URL
    CONFERENCE_ID = 1
    SECRET_KEY = 'LWd2tzlprdGHCIPHTd4tp5SBFgDszm'
    SERVICE_BUS_CONNECTION_STRING = os.getenv('TECHCONF_NOTIFICATION_CONNECTION_STRING')
    SERVICE_BUS_QUEUE_NAME = 'notification'


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False
