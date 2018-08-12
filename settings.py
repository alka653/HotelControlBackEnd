from flask_socketio import SocketIO
from flask_cors import CORS
from flask import Flask

class Settings(object):
	SQLALCHEMY_DATABASE_URI = 'postgres://cybfnbxocsfzxy:8b42d04267cca4592f6e1ae935f68ba781845906d82c381770733b03a8a7f8a5@ec2-23-23-216-40.compute-1.amazonaws.com:5432/deqgb8ip943hjj'
	#SQLALCHEMY_DATABASE_URI = 'postgres://admin:xrpw&f5cJuBg2XjS@localhost:5432/hotelcontrol_db'
	SECRET_KEY = 'Vh@$!LQMauYcnLrK4=aLW*4R%kcT@x'
	DEBUG = True

application = Flask(__name__)
application.config.from_object(Settings)
CORS(application)
socketio = SocketIO(application)