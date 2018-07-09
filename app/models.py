# -*- encoding: utf-8 -*-
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from flask_sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt
from slugify import slugify
from constants import *
from settings import *
from utils import *
import datetime
import random
import time

db = SQLAlchemy(application)
bcrypt = Bcrypt(application)

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key = True, autoincrement = True)
	nombre = db.Column(db.String(50))
	username = db.Column(db.String(32), index = True)
	password_hash = db.Column(db.String(255))
	token = db.Column(db.String(300))

	def __init__(self, username, nombre, password):
		self.username = username
		self.nombre = nombre
		self.password_hash = password

	def generate_token(self):
		return Serializer(Settings.SECRET_KEY).dumps({'id': self['id']})

	def verify_password(self, password):
		return bcrypt.check_password_hash(self.password_hash, password)

	@staticmethod
	def verify_auth_token(token):
		s = Serializer(Settings.SECRET_KEY)
		try:
			data = s.loads(token)
		except SignatureExpired:
			return None
		except BadSignature:
			return None
		user = User.query.get(data['id'])
		return user

	@staticmethod
	def update(self):
		token = Serializer(Settings.SECRET_KEY).dumps({'id': self['id']})
		user = User.query.filter_by(id = self['id']).first()
		user.token = token
		db.session.commit()
		return token

	@staticmethod
	def save(self):
		password = str(random.randint(100000, 999999))
		data = User(username = self['username'], nombre = self['nombre'], password = bcrypt.generate_password_hash(password))
		db.session.add(data)
		db.session.commit()
		print(password)
		return data

class Estado(db.Model):
	__tablename__ = 'estados'
	id = db.Column(db.Integer, primary_key = True, autoincrement = True)
	nombre_estado = db.Column(db.String(20))
	slug_estado = db.Column(db.String(40))

	def __init__(self, id, nombre_estado, slug_estado):
		self.id = id
		self.nombre_estado = nombre_estado
		self.slug_estado = slug_estado

	@staticmethod
	def save(self):
		data = Estado(id = self['id'], nombre_estado = self['nombre_estado'], slug_estado = slugify(self['nombre_estado']))
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

	def get_all_serialize(self, area_id = '', tipo_sensor_id = ''):
		data = {
			'nombre_tipo': self.nombre_tipo,
			'slug_tipo': self.slug_tipo
		}
		if(area_id != ''):
			data['consumo_promedio'] = consumo_promedio(area_id, tipo_sensor_id, 'now', Sensor, SensorMedida)
		return data

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

class PrecioConsumoMes(db.Model):
	__tablename__ = 'precios_consumos_mes'
	id = db.Column(db.Integer, primary_key = True, autoincrement = True)
	mes = db.Column(db.String(1))
	tipo_sensor_id = db.Column(db.Integer, db.ForeignKey('tipos_sensores.id'))
	precio_base = db.Column(db.Float(precision = 2))
	fecha_ingreso = db.Column(db.DateTime, default = datetime.datetime.now())
	fecha_modificado = db.Column(db.DateTime, nullable = True)

	def __init__(self, mes, tipo_sensor_id, precio_base, fecha_ingreso):
		self.mes = mes
		self.tipo_sensor_id = tipo_sensor_id
		self.precio_base = precio_base
		self.fecha_ingreso = fecha_ingreso

	@staticmethod
	def save(self):
		data = PrecioConsumoMes(mes = self['mes'], tipo_sensor_id = self['tipo_sensor_id'], precio_base = self['precio_base'], fecha_ingreso = datetime.datetime.now())
		db.session.add(data)
		db.session.commit()
		return data

	@staticmethod
	def update(self, id):
		precio_consumo_mes = PrecioConsumoMes.query.filter_by(id = id).first()
		precio_consumo_mes.precio_base = self['precio_base']
		precio_consumo_mes.tipo_sensor_id = self['tipo_sensor_id']
		precio_consumo_mes.fecha_modificado = datetime.datetime.now()
		db.session.commit()
		return True

	def get_all_serialize(self):
		data = {
			'mes': DATA_MONTHS[int(self.mes)],
			'tipo_sensor': {'nombre_tipo': TipoSensor.query.filter_by(id = self.tipo_sensor_id).first().nombre_tipo, 'id_tipo': self.tipo_sensor_id},
			'precio_base': self.precio_base,
			'fecha_ingreso': str(self.fecha_ingreso.year)+'/'+str(self.fecha_ingreso.month)+'/'+str(self.fecha_ingreso.day),
			'fecha_modificado': (str(self.fecha_modificado.year)+'/'+str(self.fecha_modificado.month)+'/'+str(self.fecha_modificado.day) if self.fecha_modificado else '-')
		}
		return data

class Area(db.Model):
	__tablename__ = 'areas'
	id = db.Column(db.Integer, primary_key = True, autoincrement = True)
	nombre_area = db.Column(db.String(50))
	slug_area = db.Column(db.String(100))
	estado_id = db.Column(db.Integer, db.ForeignKey('estados.id'))
	areas_consumos_tolerables = db.relationship('AreaConsumoTolerable', backref = 'area', lazy = 'dynamic')

	def __init__(self, id, nombre_area, estado_id, slug_area):
		self.nombre_area = nombre_area
		self.estado_id = estado_id
		self.slug_area = slug_area
		self.id = id

	@staticmethod
	def save(self):
		data = Area(nombre_area = self['nombre_area'], estado_id = 1, slug_area = slugify(self['nombre_area']))
		db.session.add(data)
		db.session.commit()
		return data

	@staticmethod
	def update(self, slug_old):
		new_slug_area = slugify(self['nombre_area'])
		area = Area.query.filter_by(slug_area = slug_old).first()
		area.nombre_area = self['nombre_area']
		area.slug_area = new_slug_area
		db.session.commit()
		return new_slug_area

	@staticmethod
	def delete_all():
		db.session.query(Area).delete()
		db.session.commit()

	def get_all_serialize(self, mode):
		data = {
			'slug_area': self.slug_area,
			'nombre_area': self.nombre_area,
			'consumo_tolerable': [consumo.get_all_serialize() for consumo in self.areas_consumos_tolerables],
			'sensores': [sensor.get_all_serialize() for sensor in Sensor.query.filter_by(area_id = self.id)],
			'total_sensores': Sensor.query.filter_by(area_id = self.id).count()
		}
		if mode == 'true':
			if Sensor.query.filter_by(area_id = self.id).count() == 0 or len(data['consumo_tolerable']) == 0:
				data = ''
		return data

class AreaConsumoTolerable(db.Model):
	__tablename__ = 'areas_consumos_tolerables'
	id = db.Column(db.Integer, primary_key = True, autoincrement = True)
	area_id = db.Column(db.Integer, db.ForeignKey('areas.id'))
	tipo_sensor_id = db.Column(db.Integer, db.ForeignKey('tipos_sensores.id'))
	medida_tolerable = db.Column(db.Float(precision = 2))

	def __init__(self, area_id, tipo_sensor_id, medida_tolerable):
		self.area_id = area_id
		self.tipo_sensor_id = tipo_sensor_id
		self.medida_tolerable = medida_tolerable

	def get_all_serialize(self):
		tipo_sensor = TipoSensor.query.filter_by(id = self.tipo_sensor_id).first()
		return {
			'tipo_sensor': tipo_sensor.get_all_serialize(self.area_id, self.tipo_sensor_id)
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
	tipo_sensor = db.relationship('TipoSensor', backref = 'tipo_sensor')
	estado_id = db.Column(db.Integer, db.ForeignKey('estados.id'))
	area_id = db.Column(db.Integer, db.ForeignKey('areas.id'))
	area = db.relationship('Area', backref = 'area')

	def __init__(self, identificacion_sensor, area_id, tipo_sensor_id, estado_id):
		self.identificacion_sensor = identificacion_sensor
		self.tipo_sensor_id = tipo_sensor_id
		self.estado_id = estado_id
		self.area_id = area_id

	def get_all_serialize(self):
		return {
			'identificacion_sensor': self.identificacion_sensor,
			'tipo_sensor': self.tipo_sensor.nombre_tipo,
			'slug_tipo': self.tipo_sensor.slug_tipo
		}

	@staticmethod
	def delete_all():
		db.session.query(Sensor).delete()
		db.session.commit()

	@staticmethod
	def save(self):
		data = Sensor(identificacion_sensor = self['identificacion_sensor'], tipo_sensor_id = self['tipo_sensor_id'], estado_id = self['estado_id'], area_id = self['area_id'])
		db.session.add(data)
		db.session.commit()
		return data

class SensorMedida(db.Model):
	id = db.Column(db.Integer, primary_key = True, autoincrement = True)
	sensor_id = db.Column(db.Integer(), db.ForeignKey('sensores.id'))
	medida_sensor = db.Column(db.Float(precision = 2))
	fecha = db.Column(db.DateTime, default = datetime.datetime.now())

	def __init__(self, sensor_id, medida_sensor, fecha):
		self.sensor_id = sensor_id
		self.medida_sensor = medida_sensor
		self.fecha = fecha

	def get_all_serialize(self):
		return {
			'medida_sensor': self.medida_sensor,
			'fecha': time.mktime(self.fecha.timetuple())
		}

	@staticmethod
	def delete_all():
		db.session.query(SensorMedida).delete()
		db.session.commit()

	@staticmethod
	def save(self):
		data = SensorMedida(sensor_id = self['sensor_id'], medida_sensor = self['medida_sensor'], fecha = datetime.datetime.now())
		db.session.add(data)
		db.session.commit()
		return data