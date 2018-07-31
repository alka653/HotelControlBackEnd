# -*- encoding: utf-8 -*-
from passlib.apps import custom_app_context as pwd_context
from flask import Blueprint, request, jsonify, g, abort
from flask_httpauth import HTTPTokenAuth
from boltons.iterutils import remap
from flask_socketio import emit
from settings import socketio
from .models import *
from .utils import *
import json

rest_api = Blueprint('rest_api', __name__)
auth = HTTPTokenAuth(scheme = 'Token')

# Model.query.filter_by
# Model.query.join(ModelForeignKey).add_columns()

"""@socketio.on('send_data', namespace = '/area/promedio/<slug_sensor>/<slug_area>')
def consumo(slug_sensor, slug_area):
	emit("consumoPromedioGeneral", consumo_promedio(slug_area, slug_sensor, 'now', Sensor, SensorMedida))"""

"""@socketio.on('send_data_graph', namespace = '/sensor/consumo/<identificacion_sensor>')
def consumo_grafico_real(identificacion_sensor):
	emit("consumoGraficoReal", consumo_real(identificacion_sensor))"""

@rest_api.route('/type-sensor', methods = ['GET'])
def list_type_sensor():
	return jsonify({'object': [object_data.get_all_serialize() for object_data in TipoSensor.query.all()]})

@rest_api.route('/area/<mode>', methods = ['GET'])
def list_areas(mode):
	drop_falsey = lambda path, key, value: bool(value)
	query = Area.query.filter_by(estado_id = 1)
	data = [object_data.get_all_serialize(mode) for object_data in (query if request.args.get('slug_area') is None else query.filter_by(slug_area = request.args.get('slug_area')))]
	return jsonify({'object': remap(data, visit = drop_falsey)})

@rest_api.route('/area/<slug_area>/sensor/guardar', methods = ['POST'])
def receive_sensor_area(slug_area):
	data = json.loads(request.data)
	area_id = Area.query.filter_by(slug_area = slug_area).first().id
	identificacion_sensor = data['identificacion_sensor']
	tipo_sensor_id = TipoSensor.query.filter_by(slug_tipo = data['tipo_sensor']).first().id
	Sensor.save({'identificacion_sensor': identificacion_sensor, 'tipo_sensor_id': tipo_sensor_id, 'area_id': area_id, 'estado_id': 1})
	return jsonify({'response': 'Sensor guardado con éxito'})

@rest_api.route('/sensor/<identificacion_sensor>/consumo-dia', methods = ['GET'])
def consumo_detallado_dia(identificacion_sensor):
	return jsonify(consumo_real(identificacion_sensor, Sensor, SensorMedida, 'json'))

@rest_api.route('/area/consumo/<identificacion_sensor>/<consumo>', methods = ['GET'])
def consumo_promedio_area(identificacion_sensor, consumo):
	sensor = Sensor.query.filter_by(identificacion_sensor = identificacion_sensor).first()
	sensor_medida = SensorMedida.save({'sensor_id': sensor.id, 'medida_sensor': consumo})
	socketio.emit('consumoPromedioGeneral', consumo_promedio(sensor.area.id, sensor.tipo_sensor.id, 'now', Sensor, SensorMedida), namespace = '/area/promedio/'+sensor.tipo_sensor.slug_tipo+'/'+sensor.area.slug_area)
	socketio.emit('consumoGraficoReal', consumo_real(sensor.identificacion_sensor, Sensor, SensorMedida), namespace = '/sensor/consumo/'+sensor.identificacion_sensor)
	return jsonify({'response': 'Dato guardado con exito'})

@rest_api.route('/area/guardar', methods = ['POST'])
def receive_new_area_name():
	nombre_area = json.loads(request.data)['nombre_area']
	Area.save({'nombre_area': nombre_area})
	return jsonify({'response': 'Área guardada con éxito'})

@rest_api.route('/area/actualizar/<slug_area_old>', methods = ['POST'])
def receive_update_area_name(slug_area_old):
	nombre_area = json.loads(request.data)['nombre_area']
	slug_area = Area.update({'nombre_area': nombre_area}, slug_area_old)
	return jsonify({'response': 'Área guardada con éxito', 'slug_area': slug_area})

@rest_api.route('/configuracion/precio-consumo', methods = ['GET'])
def lista_precio_consumo():
	drop_falsey = lambda path, key, value: bool(value)
	query = PrecioConsumoMes.query
	data = {}
	for object_data in query:
		content_data = object_data.get_all_serialize()
		data[content_data['id']] = content_data
	return jsonify({'object': data})

@rest_api.route('/configuracion/precio-consumo', methods = ['POST'])
def precio_consumo_save():
	date_now = datetime.datetime.now()
	message = 'Datos guardados con éxito'
	data = json.loads(request.data)
	tipo_sensor_id = TipoSensor.query.filter_by(slug_tipo = data['tipo_sensor']).first().id
	if PrecioConsumoMes.query.filter(extract('year', PrecioConsumoMes.fecha_ingreso) == date_now.year).filter_by(mes = data['mes'], tipo_sensor_id = tipo_sensor_id).count() > 0:
		message = 'Ya se encuentra ingresado un costo en el mes seleccionado'
	else:
		PrecioConsumoMes.save({'mes': data['mes'], 'tipo_sensor_id': tipo_sensor_id, 'precio_base': float(data['precio_base'])})
	return jsonify({'response': message})

@rest_api.route('/configuracion/precio-consumo/<precio_consumo_id>', methods = ['POST'])
def precio_consumo_update(precio_consumo_id):
	data = json.loads(request.data)
	tipo_sensor_id = TipoSensor.query.filter_by(slug_tipo = data['tipo_sensor']).first().id
	PrecioConsumoMes.update({'mes': data['mes'], 'tipo_sensor_id': tipo_sensor_id, 'precio_base': float(data['precio_base'])}, precio_consumo_id)
	return jsonify({'response': 'Datos actualizados con éxito'})

@rest_api.route('/configuracion/precio-consumo/<precio_consumo_id>/eliminar', methods = ['GET'])
def precio_consumo_delete(precio_consumo_id):
	PrecioConsumoMes.delete(precio_consumo_id)
	return jsonify({'response': 'Eliminado con éxito'})

# LATER

@rest_api.route('/auth/login', methods = ['POST'])
def auth_login():
	response = {}
	content_data = json.loads(request.data)
	user = User.query.filter_by(username = content_data['username']).first()
	if user is not None:
		if user.verify_password(content_data['password']):
			token = User.update({'id': user.id})
			response = {'response': 'success', 'msg': 'Ingreso exitoso', 'token': token}
		else:
			response = {'response': 'error', 'msg': 'Contraseña incorrecta'}
	else:
		response = {'response': 'error', 'msg': 'Usuario no existente'}
	return jsonify(response)

@rest_api.route('/auth/register', methods = ['POST'])
def auth_register():
	response = {}
	content_data = json.loads(request.data)
	username = content_data['username']
	nombre = content_data['nombre']
	if username is None or nombre is None:
		response = {'reponse': 'error', 'msg': 'Error al crear el usuario'}
	else:
		if User.query.filter_by(username = username).first() is None:
			user = User.save({'username': username, 'nombre': nombre})
			response = {'response': 'success', 'msg': 'Exito al crear el usuario', 'token': user.token}
		else:
			response = {'response': 'error', 'msg': 'El usuario ya se encuentra creado'}
	return jsonify(response)