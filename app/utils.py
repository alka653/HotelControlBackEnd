from sqlalchemy import func, DATE, cast, extract
from datetime import date
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
	return '{"consumo_promedio_dia":'+str(round(valor_promedio / (contador if contador > 0 else 1), 2))+', "consumo_maximo_dia":'+str(valor_maximo_consumo)+', "consumo_promedio_mensual": '+str(consumo_promedio_mensual)+'}'

def consumo_real(identificacion_sensor, Sensor, SensorMedida, date_sql):
	date_sql = date_sql if date_sql != 'now' else date.today()
	sensor_id = Sensor.query.filter_by(identificacion_sensor = identificacion_sensor).first().id
	return {'object': [object_data.get_all_serialize() for object_data in SensorMedida.query.filter_by(sensor_id = sensor_id).filter(cast(SensorMedida.fecha, DATE) == date.today()).order_by('fecha ASC')]}