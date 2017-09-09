from flask import Blueprint, request, jsonify, abort
from flask_socketio import emit
from settings import socketio
from flask import request
from models import *
from utils import *

rest_api = Blueprint('rest_api', __name__)

# Model.query.filter_by
# Model.query.join(ModelForeignKey).add_columns()

@rest_api.route('/area', methods = ['GET'])
def list_areas():
	return jsonify({'object': [object_data.get_all_serialize() for object_data in Area.query.filter_by(estado_id = 1).order_by('id asc')]})

@socketio.on('connect', namespace = '/area/promedio/<slug_sensor>/<slug_area>')
def consumo(slug_sensor, slug_area):
	emit("consumoPromedioGeneral", consumo_promedio(slug_area, slug_sensor, 'now', Sensor, SensorMedida))

@rest_api.route('/area/consumo/<identificacion_sensor>/<consumo>', methods = ['GET'])
def consumo_promedio_area(identificacion_sensor, consumo):
	sensor = Sensor.query.filter_by(identificacion_sensor = identificacion_sensor).first()
	sensor_medida = SensorMedida.save({'sensor_id': sensor.id, 'medida_sensor': consumo})
	socketio.emit('consumoPromedioGeneral', consumo_promedio(sensor.area.id, sensor.tipo_sensor.id, 'now', Sensor, SensorMedida), namespace = '/area/promedio/'+sensor.tipo_sensor.slug_tipo+'/'+sensor.area.slug_area)
	return jsonify({'response': 'Dato guardado con exito'})