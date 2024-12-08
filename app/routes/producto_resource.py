from flask import Blueprint, jsonify, request

from app.mapping import ProductoSchema
from app.services import ProductoService

Producto = Blueprint('Producto', __name__)
service = ProductoService()
Producto_schema =ProductoSchema()

"""
Obtiene todos las Producto
"""
@Producto.route('/Producto', methods=['GET'])
def all():
    resp = Producto_schema.dump(service.get_all(), many=True) 
    return resp, 200

"""
Obtiene una Producto por id
"""
@Producto.route('/Producto/<int:id>', methods=['GET'])
def one(id):
    resp = Producto_schema.dump(service.get_by_id(id)) 
    return resp, 200

"""
Crea nueva Producto
"""
@Producto.route('/Producto', methods=['POST'])
def create():
    Producto = Producto_schema.load(request.json)
    resp = Producto_schema.dump(service.create(Producto))
    return resp, 201

"""
Actualiza una Producto existente
"""
@Producto.route('/Producto/<int:id>', methods=['PUT'])
def update(id):
    Producto = Producto_schema.load(request.json)
    resp = Producto_schema.dump(service.update(id, Producto))
    return resp, 200

"""
Elimina una Producto existente
"""
@Producto.route('/Producto/<int:id>', methods=['DELETE'])
def delete(id):
    msg = "Producto eliminado correctamente"
    resp = service.delete(id)
    if not resp:
        msg = "No se pudo eliminar el Producto"
    return jsonify(msg), 204