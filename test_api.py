from .settings import application
from flask import request, Flask
import pytest

def create_app(config_filename=None):
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_pyfile(config_filename)
	initialize_extensions(app)
	register_blueprints(app)
	return app

@pytest.fixture(scope='module')
def test_client():
	flask_app = create_app('flask_test.cfg')
	# Flask provides a way to test your application by exposing the Werkzeug test Client
	# and handling the context locals for you.
	testing_client = flask_app.test_client()
	# Establish an application context before running the tests.
	ctx = flask_app.app_context()
	ctx.push()
	yield testing_client  # this is where the testing happens!
	ctx.pop()

def test_type_sensor(test_client):
	response = test_client.get('/type-sensor')
	assert response.status_code == 200