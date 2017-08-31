from app.models import *
import click

@click.command()
def delete_data():
	SensorMedida.delete_all()
	click.echo('Medidas eliminados')
	Sensor.delete_all()
	click.echo('Sensores eliminados')
	AreaConsumoTolerable.delete_all()
	click.echo('Tolerables eliminados')
	Area.delete_all()
	click.echo('Areas eliminados')
	Estado.delete_all()
	click.echo('Estados eliminados')
	TipoSensor.delete_all()
	click.echo('Tipos de sensores eliminados')

if __name__ == '__main__':
	delete_data()