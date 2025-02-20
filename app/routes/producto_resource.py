from flask import Blueprint, request
from marshmallow import ValidationError
from app import limiter
from app.mapping import ProductoSchema, ResponseSchema
from app.services import ProductoService, ResponseBuilder

Producto = Blueprint('Producto', __name__)
service = ProductoService()
producto_schema = ProductoSchema()
response_schema = ResponseSchema()

# Aplicar limitadores específicos en las rutas
@Producto.route('/producto', methods=['GET'])
@limiter.limit("5 per minute")  # Límite específico para esta ruta
def all():
    response_builder = ResponseBuilder()
    try:
        data = producto_schema.dump(service.all(), many=True)
        response_builder.add_message("Productos found").add_status_code(200).add_data(data)
        return response_schema.dump(response_builder.build()), 200
    except Exception as e:
        response_builder.add_message("Error fetching Productos").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Producto.route('/producto/<int:id>', methods=['GET'])
@limiter.limit("5 per minute")
def find(id):
    response_builder = ResponseBuilder()
    try:
        data = service.find(id)
        if data:
            serialized_data = producto_schema.dump(data)
            response_builder.add_message("Producto found").add_status_code(200).add_data(serialized_data)
            return response_schema.dump(response_builder.build()), 200
        else:
            response_builder.add_message("Producto not found").add_status_code(404).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 404
    except Exception as e:
        response_builder.add_message("Error fetching Producto").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Producto.route('/producto', methods=['POST'])
@limiter.limit("5 per minute")
def add():
    response_builder = ResponseBuilder()
    try:
        json_data = request.json
        if not json_data:
            raise ValidationError("No data provided")

        producto = producto_schema.load(json_data)
        data = producto_schema.dump(service.add(producto))
        response_builder.add_message("Producto created").add_status_code(201).add_data(data)
        return response_schema.dump(response_builder.build()), 201
    except ValidationError as err:
        response_builder.add_message("Validation error").add_status_code(422).add_data(err.messages)
        return response_schema.dump(response_builder.build()), 422
    except Exception as e:
        response_builder.add_message("Error creating Producto").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Producto.route('/producto/<int:id>', methods=['PUT'])
@limiter.limit("5 per minute")
def update(id):
    response_builder = ResponseBuilder()
    try:
        if not service.find(id):
            response_builder.add_message("Producto not found").add_status_code(404).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 404

        json_data = request.json
        if not json_data:
            raise ValidationError("No data provided")

        producto = producto_schema.load(json_data)
        data = producto_schema.dump(service.update(id, producto))
        response_builder.add_message("Producto updated").add_status_code(200).add_data(data)
        return response_schema.dump(response_builder.build()), 200
    except ValidationError as err:
        response_builder.add_message("Validation error").add_status_code(422).add_data(err.messages)
        return response_schema.dump(response_builder.build()), 422
    except Exception as e:
        response_builder.add_message("Error updating Producto").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Producto.route('/producto/<int:id>', methods=['DELETE'])
@limiter.limit("3 per minute")  # Menos llamadas permitidas para eliminar
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
