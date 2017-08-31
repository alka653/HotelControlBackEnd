from flask import Blueprint, request, jsonify, abort
from models import *

rest_api = Blueprint('rest_api', __name__)

# Model.query.filter_by
# Model.query.join(ModelForeignKey).add_columns()

@rest_api.route('/', methods = ['GET'])
def show_entries():
	return jsonify({'message': 'Oe'})

@rest_api.route('/area', methods = ['GET'])
def list_areas():
	return jsonify({'object': [object_data.get_all_serialize() for object_data in Area.query.filter_by(estado_id = 1)]})