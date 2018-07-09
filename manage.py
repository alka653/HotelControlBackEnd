from app.views import rest_api
from app.models import db
from settings import *

application.register_blueprint(rest_api)

if __name__ == "__main__":
	db.init_app(application)

	with application.app_context():
		db.create_all()

	#application.run(debug = Settings.DEBUG, port = 8000)
	socketio.run(application, host = "0.0.0.0")