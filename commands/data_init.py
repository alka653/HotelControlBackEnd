from app.models import *
import click

@click.command()
def data_init():
	estado_activo = Estado.save({'nombre_estado': 'Activo'})
	estado_inactivo = Estado.save({'nombre_estado': 'Inactivo'})
	click.echo('Estados creados')
	tipo_agua = TipoSensor.save({'nombre_tipo': 'Agua'})
	tipo_energia = TipoSensor.save({'nombre_tipo': 'energia'})
	click.echo('Tipos de sensores creados')
	area_1 = Area.save({'nombre_area': 'Lavanderia', 'estado_id': estado_activo.id})
	area_2 = Area.save({'nombre_area': 'Juntas', 'estado_id': estado_activo.id})
	click.echo('Areas creados')
	AreaConsumoTolerable.save({'area_id': area_1.id, 'tipo_sensor_id': tipo_agua.id, 'medida_tolerable': 5.18})
	AreaConsumoTolerable.save({'area_id': area_1.id, 'tipo_sensor_id': tipo_energia.id, 'medida_tolerable': 15})
	AreaConsumoTolerable.save({'area_id': area_2.id, 'tipo_sensor_id': tipo_agua.id, 'medida_tolerable': 5.18})
	AreaConsumoTolerable.save({'area_id': area_2.id, 'tipo_sensor_id': tipo_energia.id, 'medida_tolerable': 15})
	click.echo('Consumo tolerable creados')

if __name__ == '__main__':
	data_init()