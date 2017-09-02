from flask import Blueprint, request, jsonify, abort
from flask_socketio import emit
from settings import socketio
from models import *

rest_api = Blueprint('rest_api', __name__)

# Model.query.filter_by
# Model.query.join(ModelForeignKey).add_columns()

@rest_api.route('/area', methods = ['GET'])
def list_areas():
	return jsonify({'object': [object_data.get_all_serialize() for object_data in Area.query.filter_by(estado_id = 1).order_by('id asc')]})

@socketio.on('connect', namespace = '/area/promedio')
def consumo_promedio():
	emit("timer", 'Que hace')

@rest_api.route('/area/prueba/<param>', methods = ['GET'])
def prueba_url(param):
	socketio.emit('timer', param, namespace = '/area/promedio')
	return jsonify({'object': param})