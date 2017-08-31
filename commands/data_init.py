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

if __name__ == '__main__':
	data_init()