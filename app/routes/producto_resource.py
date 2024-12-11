from flask import Blueprint, request
from marshmallow import ValidationError

from app.mapping import ProductoSchema, ResponseSchema
from app.services import ProductoService, ResponseBuilder

Producto = Blueprint('Producto', __name__)
service = ProductoService()
Producto_schema = ProductoSchema()
response_schema = ResponseSchema()

@Producto.route('/Producto', methods=['GET'])
def all():
    response_builder = ResponseBuilder()
    try:
        data = Producto_schema.dump(service.get_all(), many=True)
        response_builder.add_message("Productos found").add_status_code(200).add_data(data)
        return response_schema.dump(response_builder.build()), 200
    except Exception as e:
        response_builder.add_message("Error fetching Productos").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Producto.route('/Producto/<int:id>', methods=['GET'])
def one(id):
    response_builder = ResponseBuilder()
    try:
        data = service.get_by_id(id)
        if data:
            serialized_data = Producto_schema.dump(data)
            response_builder.add_message("Producto found").add_status_code(200).add_data(serialized_data)
            return response_schema.dump(response_builder.build()), 200
        else:
            response_builder.add_message("Producto not found").add_status_code(404).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 404
    except Exception as e:
        response_builder.add_message("Error fetching Producto").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Producto.route('/Producto', methods=['POST'])
def create():
    response_builder = ResponseBuilder()
    try:
        producto = Producto_schema.load(request.json)
        data = Producto_schema.dump(service.create(producto))
        response_builder.add_message("Producto created").add_status_code(201).add_data(data)
        return response_schema.dump(response_builder.build()), 201
    except ValidationError as err:
        response_builder.add_message("Validation error").add_status_code(422).add_data(err.messages)
        return response_schema.dump(response_builder.build()), 422
    except Exception as e:
        response_builder.add_message("Error creating Producto").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Producto.route('/Producto/<int:id>', methods=['PUT'])
def update(id):
    response_builder = ResponseBuilder()
    try:
        producto = Producto_schema.load(request.json)
        data = Producto_schema.dump(service.update(id, producto))
        response_builder.add_message("Producto updated").add_status_code(200).add_data(data)
        return response_schema.dump(response_builder.build()), 200
    except ValidationError as err:
        response_builder.add_message("Validation error").add_status_code(422).add_data(err.messages)
        return response_schema.dump(response_builder.build()), 422
    except Exception as e:
        response_builder.add_message("Error updating Producto").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Producto.route('/Producto/<int:id>', methods=['DELETE'])
def delete(id):
    response_builder = ResponseBuilder()
    try:
        if service.delete(id):
            response_builder.add_message("Producto deleted").add_status_code(200).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 200
        else:
            response_builder.add_message("Producto not found").add_status_code(404).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 404
    except Exception as e:
        response_builder.add_message("Error deleting Producto").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500
