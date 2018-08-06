from sqlalchemy import func, DATE, cast, extract, TIMESTAMP
from datetime import date, datetime
from flask import jsonify

def consumo_promedio(area_id, tipo_sensor_id, date_sql, Sensor, SensorMedida):
	contador = 0
	valor_promedio = 0
	valor_maximo_consumo = 0
	consumo_promedio_mensual = 0
	date_sql = date_sql if date_sql != 'now' else date.today()
	for sensor in Sensor.query.filter_by(tipo_sensor_id = tipo_sensor_id, area_id = area_id):
		for promedio in SensorMedida.query.filter_by(sensor_id = sensor.id).filter(cast(SensorMedida.fecha, DATE) == date.today()).all():
			contador += 1
			valor_promedio += promedio.medida_sensor
			valor_maximo_consumo = promedio.medida_sensor if promedio.medida_sensor > valor_maximo_consumo else valor_maximo_consumo
		consumo_promedio_mensual = SensorMedida.query.filter_by(sensor_id = sensor.id).filter(extract('year', SensorMedida.fecha) == date.today().year, extract('month', SensorMedida.fecha) == date.today().month).value(func.avg(SensorMedida.medida_sensor))
	return '{"consumo_promedio_dia":'+str(round(valor_promedio / (contador if contador > 0 else 1), 2))+', "consumo_maximo_dia":'+str(round(valor_maximo_consumo, 2))+', "consumo_promedio_mensual": '+str(round(consumo_promedio_mensual, 2) if consumo_promedio_mensual is not None else 0)+'}'

def comsumo_promedio_por_mes(mes, fecha, tipo_sensor_id, Sensor, SensorMedida):
	conteo = 0
	promedio = 0
	last_date = []
	suma_total = 0
	suma_dia = 0
	last_date_know = []
	anio = fecha.split('/')
	sensor_list = [sensor.id for sensor in Sensor.query.filter_by(tipo_sensor_id = tipo_sensor_id).order_by('tipo_sensor_id ASC').all()]
	for object_data in SensorMedida.query.filter(SensorMedida.sensor_id.in_(sensor_list)).filter(extract('year', SensorMedida.fecha) == anio[0]).filter(extract('month', SensorMedida.fecha) == mes).order_by('fecha ASC').all():
		content = object_data.get_all_serialize()
		last_date = content['fecha'].split(':')
		if last_date_know:
			if last_date_know[2] == last_date[2]:
				promedio += content['medida_sensor']
				conteo += 1
				if last_date_know[3] != last_date[3]:
					suma_dia += (promedio / conteo)
					promedio = 0
					conteo = 1
			else:
				if suma_dia > 0:
					if suma_total > 0:
						suma_total += suma_dia
					else:
						suma_total += (promedio / conteo) + suma_dia
					suma_dia = 0
				else:
					suma_total += (promedio / conteo)
				promedio = content['medida_sensor']
				conteo = 1
				last_date_know = last_date
		else:
			conteo += 1
			promedio += content['medida_sensor']
		last_date_know = last_date
	suma_total += (promedio / conteo)
	return suma_total

def consumo_real(identificacion_sensor, Sensor, SensorMedida, all_data = ''):
	data = []
	last_date = []
	promedio = 0
	conteo = 0
	#date_sql = date_sql if date_sql != 'now' else date.today()
	sensor_id = Sensor.query.filter_by(identificacion_sensor = identificacion_sensor).first().id
	for object_data in SensorMedida.query.filter_by(sensor_id = sensor_id).filter(cast(SensorMedida.fecha, DATE) == date.today()).order_by('fecha ASC'):
		response = group_querie_date(last_date, object_data, conteo, promedio, data)
		last_date = response['last_date']
		object_data = response['object_data']
		conteo = response['conteo']
		promedio = response['promedio']
		data = response['data']
	if all_data == '':
		#data = response['data']
		if data:
			data = data[-1]
	return {'object': data}
	#return {'object': [object_data.get_all_serialize() for object_data in ]}

def group_querie_date(last_date, object_data, conteo, promedio, data):
	content = object_data.get_all_serialize()
	date_split = content['fecha'].split(':')
	if last_date:
		if last_date[3] == date_split[3] and last_date[4] == date_split[4]:
			conteo += 1
			promedio += content['medida_sensor']
		elif promedio != 0 and conteo != 0:
			data.append({
				'medida_sensor': (promedio / conteo),
				'fecha': last_date[0]+':'+last_date[1]+':'+last_date[2]+':'+last_date[3]+':'+last_date[4]
			})
			promedio = 0
			conteo = 0
		last_date = date_split
	else:
		last_date = date_split
	return {
		'last_date': last_date,
		'object_data': object_data,
		'conteo': conteo,
		'promedio': promedio,
		'data': data
	}