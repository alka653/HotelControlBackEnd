from flask import Flask

class Settings(object):
	SQLALCHEMY_DATABASE_URI = 'postgres://admin:xrpw&f5cJuBg2XjS@localhost:5432/hotelcontrol_db'
	SECRET_KEY = 'Vh@$!LQMauYcnLrK4=aLW*4R%kcT@x'
	DEBUG = True

application = Flask(__name__)
application.config.from_object(Settings)