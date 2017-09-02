from flask_sqlalchemy import SQLAlchemy
from settings import application
from slugify import slugify
import datetime

db = SQLAlchemy(application)

class Estado(db.Model):
	__tablename__ = 'estados'
	id = db.Column(db.Integer, primary_key = True, autoincrement = True)
	nombre_estado = db.Column(db.String(20))
	slug_estado = db.Column(db.String(40))

	def __init__(self, nombre_estado, slug_estado):
		self.nombre_estado = nombre_estado
		self.slug_estado = slug_estado

	@staticmethod
	def save(self):
		data = Estado(nombre_estado = self['nombre_estado'], slug_estado = slugify(self['nombre_estado']))
		db.session.add(data)
		db.session.commit()
		return data

	@staticmethod
	def delete_all():
		db.session.query(Estado).delete()
		db.session.commit()

class TipoSensor(db.Model):
	__tablename__ = 'tipos_sensores'
	id = db.Column(db.Integer, primary_key = True, autoincrement = True)
	nombre_tipo = db.Column(db.String(20))
	slug_tipo = db.Column(db.String(40))

	def __init__(self, nombre_tipo, slug_tipo):
		self.nombre_tipo = nombre_tipo
		self.slug_tipo = slug_tipo

	def get_all_serialize(self):
		return {
			'nombre_tipo': self.nombre_tipo,
			'slug_tipo': self.slug_tipo
		}

	@staticmethod
	def save(self):
		data = TipoSensor(nombre_tipo = self['nombre_tipo'], slug_tipo = slugify(self['nombre_tipo']))
		db.session.add(data)
		db.session.commit()
		return data

	@staticmethod
	def delete_all():
		db.session.query(TipoSensor).delete()
		db.session.commit()

class Area(db.Model):
	__tablename__ = 'areas'
	id = db.Column(db.Integer, primary_key = True, autoincrement = True)
	nombre_area = db.Column(db.String(50))
	slug_area = db.Column(db.String(100))
	estado_id = db.Column(db.Integer, db.ForeignKey('estados.id'))
	areas_consumos_tolerables = db.relationship('AreaConsumoTolerable', backref = 'area', lazy = 'dynamic')

	def __init__(self, nombre_area, estado_id, slug_area):
		self.nombre_area = nombre_area
		self.estado_id = estado_id
		self.slug_area = slug_area

	@staticmethod
	def save(self):
		data = Area(nombre_area = self['nombre_area'], estado_id = self['estado_id'], slug_area = slugify(self['nombre_area']))
		db.session.add(data)
		db.session.commit()
		return data

	@staticmethod
	def delete_all():
		db.session.query(Area).delete()
		db.session.commit()

	def get_all_serialize(self):
		return {
			'slug_area': self.slug_area,
			'nombre_area': self.nombre_area,
			'consumo_tolerable': [consumo.get_all_serialize() for consumo in self.areas_consumos_tolerables]
		}

class AreaConsumoTolerable(db.Model):
	__tablename__ = 'areas_consumos_tolerables'
	id = db.Column(db.Integer, primary_key = True, autoincrement = True)
	area_id = db.Column(db.Integer, db.ForeignKey('areas.id'))
	tipo_sensor_id = db.Column(db.Integer, db.ForeignKey('tipos_sensores.id'))
	tipo_sensor = db.relationship('TipoSensor', backref = 'tipo_sensor')
	medida_tolerable = db.Column(db.Float(precision = 2))

	def __init__(self, area_id, tipo_sensor_id, medida_tolerable):
		self.area_id = area_id
		self.tipo_sensor_id = tipo_sensor_id
		self.medida_tolerable = medida_tolerable

	def get_all_serialize(self):
		return {
			'tipo_sensor': self.tipo_sensor.get_all_serialize()
		}

	@staticmethod
	def delete_all():
		db.session.query(AreaConsumoTolerable).delete()
		db.session.commit()

	@staticmethod
	def save(self):
		data = AreaConsumoTolerable(area_id = self['area_id'], tipo_sensor_id = self['tipo_sensor_id'], medida_tolerable = self['medida_tolerable'])
		db.session.add(data)
		db.session.commit()
		return data

class Sensor(db.Model):
	__tablename__ = 'sensores'
	id = db.Column(db.Integer, primary_key = True, autoincrement = True)
	identificacion_sensor = db.Column(db.String(10))
	tipo_sensor_id = db.Column(db.Integer, db.ForeignKey('tipos_sensores.id'))
	estado_id = db.Column(db.Integer, db.ForeignKey('estados.id'))
	area_id = db.Column(db.Integer, db.ForeignKey('areas.id'))

	def __init__(self, area_id, tipo_sensor_id):
		self.identificacion_sensor = identificacion_sensor
		self.tipo_sensor_id = tipo_sensor_id
		self.estado_id = estado_id
		self.area_id = area_id

	@staticmethod
	def delete_all():
		db.session.query(Sensor).delete()
		db.session.commit()

	@staticmethod
	def save(self):
		data = Sensor(identificacion_sensor = self['identificacion_sensor'], tipo_sensor_id = self['tipo_sensor_id'], estado_id = self['estado_id'], area_id = self['area_id'])
		db.session.add(self)
		db.session.commit()
		return data

class SensorMedida(db.Model):
	id = db.Column(db.Integer, primary_key = True, autoincrement = True)
	sensor_id = db.Column(db.Integer(), db.ForeignKey('sensores.id'))
	medida_sensor = db.Column(db.Float(precision = 2))
	fecha = db.Column(db.DateTime, default = datetime.datetime.now)

	def __init__(self, sensor_id, medida_sensor, fecha):
		self.sensor_id = sensor_id
		self.medida_sensor = medida_sensor
		self.fecha = fecha

	@staticmethod
	def delete_all():
		db.session.query(SensorMedida).delete()
		db.session.commit()

	@staticmethod
	def save(self):
		data = SensorMedida(sensor_id = self['sensor_id'], medida_sensor = self['medida_sensor'], fecha = self['fecha'])
		db.session.add(self)
		db.session.commit()
		return data