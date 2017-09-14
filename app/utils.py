from sqlalchemy import func

def consumo_promedio(area_id, tipo_sensor_id, date, Sensor, SensorMedida):
	contador = 0
	valor_promedio = 0
	for sensor in Sensor.query.filter_by(tipo_sensor_id = tipo_sensor_id, area_id = area_id):
		for promedio in SensorMedida.query.filter_by(sensor_id = sensor.id):
			contador += 1
			valor_promedio += promedio.medida_sensor
	return '{"consumo_promedio_dia":'+str(round(valor_promedio / (contador if contador > 0 else 1), 2))+'}'